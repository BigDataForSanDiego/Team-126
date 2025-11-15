# PostgreSQL with pgvector Setup Guide

This guide explains how to set up PostgreSQL with the pgvector extension for semantic search capabilities.

## What is pgvector?

pgvector is a PostgreSQL extension that adds support for vector embeddings, enabling:
- **Semantic similarity search** - Find similar messages based on meaning, not just keywords
- **Efficient vector storage** - Store 768-dimensional embeddings from Vertex AI
- **Fast similarity queries** - Use HNSW indexes for quick nearest-neighbor search

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL 15+ (recommended for best pgvector performance)

## Option 1: Docker Compose Setup (Recommended)

### 1. Update docker-compose.yml

Update your existing `docker-compose.yml` to use the pgvector-enabled PostgreSQL image:

```yaml
version: '3.8'

services:
  db:
    image: ankane/pgvector:latest  # PostgreSQL with pgvector pre-installed
    container_name: homeless_assistant_db
    environment:
      POSTGRES_DB: homeless_assistant_db
      POSTGRES_USER: homeless_assistant
      POSTGRES_PASSWORD: dev_password_change_in_production
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U homeless_assistant"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 2. Start the Database

```bash
# Stop existing database (if running)
docker-compose down

# Start new database with pgvector
docker-compose up -d

# Wait for database to be ready
docker-compose logs -f db
```

### 3. Verify pgvector Installation

```bash
# Connect to the database
docker exec -it homeless_assistant_db psql -U homeless_assistant -d homeless_assistant_db

# Enable and test pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify it works
SELECT extname FROM pg_extension WHERE extname = 'vector';

# You should see 'vector' in the output
# Exit with \q
```

## Option 2: Manual PostgreSQL Setup

If you're running PostgreSQL locally without Docker:

### macOS (Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@15

# Install pgvector
brew install pgvector

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb homeless_assistant_db

# Connect and enable extension
psql homeless_assistant_db
CREATE EXTENSION vector;
\q
```

### Ubuntu/Debian

```bash
# Install PostgreSQL 15
sudo apt update
sudo apt install postgresql-15 postgresql-server-dev-15

# Install pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Restart PostgreSQL
sudo systemctl restart postgresql

# Create database and enable extension
sudo -u postgres psql
CREATE DATABASE homeless_assistant_db;
\c homeless_assistant_db
CREATE EXTENSION vector;
\q
```

## Backend Setup

### 1. Update .env File

Ensure your `.env` file has the correct PostgreSQL connection:

```bash
# Database Configuration - PostgreSQL with pgvector
DATABASE_URL=postgresql://homeless_assistant:dev_password_change_in_production@127.0.0.1:5432/homeless_assistant_db
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The requirements.txt now includes:
- `pgvector==0.2.4` - Python client for pgvector
- `psycopg2-binary==2.9.9` - PostgreSQL adapter

### 3. Run Migrations

```bash
# Navigate to backend directory
cd backend

# Run pgvector migration
python migrate_pgvector.py
```

You should see:

```
============================================================
Starting pgvector migration...
============================================================

[1/4] Enabling pgvector extension...
✓ pgvector extension enabled
[2/4] Adding embedding column to messages table...
✓ Embedding column added to messages table
[3/4] Creating vector similarity search index...
✓ Vector similarity index created (HNSW)
[4/4] Verifying pgvector setup...
✓ pgvector setup verified successfully

============================================================
✅ pgvector migration completed!
============================================================
```

## Features Enabled

After setup, your application will have:

### 1. Automatic Embedding Generation
Every message (user and assistant) automatically gets a 768-dimensional embedding using Vertex AI's `text-embedding-004` model.

### 2. Semantic Similarity Search
Search for similar messages in a conversation:

```bash
# Example API call
curl -X POST "http://localhost:8000/conversation/1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "food assistance",
    "limit": 5,
    "threshold": 0.7
  }'
```

### 3. Vector Indexes
HNSW (Hierarchical Navigable Small World) indexes for fast similarity search on large datasets.

## Database Schema

After migration, the `messages` table will have:

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER,
    role VARCHAR,
    content TEXT,
    timestamp TIMESTAMP,
    is_voice BOOLEAN,
    latitude FLOAT,
    longitude FLOAT,
    embedding vector(768)  -- NEW: Vector embedding column
);

-- HNSW index for fast similarity search
CREATE INDEX messages_embedding_idx
ON messages
USING hnsw (embedding vector_cosine_ops);
```

## Verify Setup

### Test Embedding Generation

```bash
# Start the backend server
python main.py

# Send a test message via WebSocket
# Embeddings will be generated automatically
# Check logs for: "[Embedding] Generated embedding for user message (dim: 768)"
```

### Test Similarity Search

```python
# Python test script
import requests

# Start a conversation and send messages
# Then search for similar messages
response = requests.post(
    "http://localhost:8000/conversation/1/search",
    json={
        "query": "where can I find shelter?",
        "limit": 5,
        "threshold": 0.7
    }
)

print(response.json())
```

## Troubleshooting

### Error: "extension vector is not available"

**Solution**: pgvector extension not installed in PostgreSQL

```bash
# Docker users: Use ankane/pgvector image
docker-compose down
# Update docker-compose.yml to use ankane/pgvector:latest
docker-compose up -d

# Local users: Install pgvector following OS-specific instructions above
```

### Error: "column embedding does not exist"

**Solution**: Migration not run

```bash
cd backend
python migrate_pgvector.py
```

### Slow Similarity Searches

**Solution**: Ensure HNSW index exists

```sql
-- Connect to database
psql $DATABASE_URL

-- Check if index exists
\di messages_embedding_idx

-- If not, create it
CREATE INDEX messages_embedding_idx
ON messages
USING hnsw (embedding vector_cosine_ops);
```

## Performance Tips

### 1. Index Maintenance

```sql
-- Rebuild index if performance degrades
REINDEX INDEX messages_embedding_idx;
```

### 2. Batch Embedding Generation

For existing messages without embeddings:

```python
# Run this script in backend directory
from database import get_db, engine
from models import Message
from embeddings import generate_embedding

db = next(get_db())

# Get messages without embeddings
messages = db.query(Message).filter(Message.embedding == None).all()

for msg in messages:
    print(f"Generating embedding for message {msg.id}...")
    msg.embedding = generate_embedding(msg.content)
    db.add(msg)

    if msg.id % 10 == 0:
        db.commit()  # Commit every 10 messages

db.commit()
print(f"✓ Generated embeddings for {len(messages)} messages")
```

### 3. Monitor Index Size

```sql
-- Check index size
SELECT pg_size_pretty(pg_relation_size('messages_embedding_idx')) as index_size;
```

## Benefits of pgvector

1. **Better Context Retrieval** - Find relevant past conversations based on semantic similarity
2. **Improved AI Responses** - Use similar messages to provide better context to the AI
3. **Deduplication** - Identify duplicate or very similar questions
4. **Analytics** - Cluster and analyze common topics in conversations
5. **Recommendation** - Suggest relevant resources based on past similar queries

## Next Steps

- ✅ pgvector installed and configured
- ✅ Embeddings generated automatically for new messages
- ✅ Similarity search API endpoint available
- 🔜 Integrate similarity search into chatbot for better context
- 🔜 Add conversation topic clustering
- 🔜 Build recommendation system for resources

## Resources

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Vertex AI Text Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
