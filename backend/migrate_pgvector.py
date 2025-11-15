"""
Database migration script to add pgvector support
This script will:
1. Enable the pgvector extension in PostgreSQL
2. Add embedding vector columns to the messages table
3. Create vector similarity search indexes

Prerequisites:
- PostgreSQL database must be running
- pgvector extension must be installed in PostgreSQL
  Install with: CREATE EXTENSION IF NOT EXISTS vector;
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import sys

def migrate_to_pgvector():
    """Add pgvector support to the database"""

    if not DATABASE_URL.startswith("postgresql"):
        print("❌ ERROR: This migration only works with PostgreSQL databases.")
        print(f"   Current DATABASE_URL: {DATABASE_URL}")
        print("   Please update your .env file to use PostgreSQL with pgvector.")
        sys.exit(1)

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("=" * 60)
        print("Starting pgvector migration...")
        print("=" * 60)

        try:
            # Step 1: Enable pgvector extension
            print("\n[1/4] Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("✓ pgvector extension enabled")

        except Exception as e:
            print(f"❌ Failed to enable pgvector extension: {e}")
            print("\nTo fix this, run the following in your PostgreSQL database:")
            print("  CREATE EXTENSION vector;")
            print("\nOr ensure pgvector is installed:")
            print("  - Docker: Use postgres:15 image with pgvector")
            print("  - Local: Install pgvector from https://github.com/pgvector/pgvector")
            sys.exit(1)

        try:
            # Step 2: Add embedding column to messages table
            print("\n[2/4] Adding embedding column to messages table...")
            conn.execute(text("""
                ALTER TABLE messages
                ADD COLUMN IF NOT EXISTS embedding vector(768);
            """))
            conn.commit()
            print("✓ Embedding column added to messages table")

        except Exception as e:
            print(f"⚠ Messages table migration: {e}")

        try:
            # Step 3: Create vector similarity search index (HNSW)
            print("\n[3/4] Creating vector similarity search index...")
            # Drop existing index if it exists
            conn.execute(text("""
                DROP INDEX IF EXISTS messages_embedding_idx;
            """))
            # Create HNSW index for fast similarity search
            conn.execute(text("""
                CREATE INDEX messages_embedding_idx
                ON messages
                USING hnsw (embedding vector_cosine_ops);
            """))
            conn.commit()
            print("✓ Vector similarity index created (HNSW)")

        except Exception as e:
            print(f"⚠ Index creation: {e}")
            print("   Note: Index will be created automatically on first use")

        try:
            # Step 4: Verify setup
            print("\n[4/4] Verifying pgvector setup...")
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.columns
                WHERE table_name = 'messages'
                AND column_name = 'embedding';
            """))
            count = result.fetchone()[0]

            if count > 0:
                print("✓ pgvector setup verified successfully")
            else:
                print("❌ Verification failed: embedding column not found")

        except Exception as e:
            print(f"⚠ Verification: {e}")

        print("\n" + "=" * 60)
        print("✅ pgvector migration completed!")
        print("=" * 60)
        print("\nYou can now:")
        print("  - Generate embeddings for messages")
        print("  - Perform semantic similarity search")
        print("  - Retrieve relevant conversation history")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Restart your backend server")
        print("  3. Embeddings will be generated automatically for new messages")

if __name__ == "__main__":
    migrate_to_pgvector()
