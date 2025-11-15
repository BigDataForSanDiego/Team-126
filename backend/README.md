# Homeless Assistant Backend

FastAPI backend for the Homeless Assistant chatbot application.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Google Cloud authentication
gcloud auth application-default login

# Setup environment
cp .env.example .env
# Edit .env and add your GOOGLE_CLOUD_PROJECT

# Run server
python main.py
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Required:
- `GOOGLE_CLOUD_PROJECT` - Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION` - Vertex AI region (default: us-central1)

Optional:
- `SECRET_KEY` - JWT signing key (change in production)
- `DATABASE_URL` - Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key (for production)

## Vertex AI Setup

See [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md) for detailed setup instructions.

**Quick setup:**
1. Install gcloud CLI
2. Run `gcloud auth application-default login`
3. Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com`
4. Set project in .env: `GOOGLE_CLOUD_PROJECT=your-project-id`

## Database

SQLite is used by default. The database will be created automatically at `./homeless_assistant.db`.

To reset the database:
```bash
rm homeless_assistant.db
python main.py
```

## Face Recognition Setup

### macOS
```bash
brew install cmake
pip install face-recognition
```

### Ubuntu/Debian
```bash
sudo apt-get install cmake libopenblas-dev liblapack-dev
pip install face-recognition
```

### Windows
```bash
# Install Visual Studio Build Tools first
# Then:
pip install face-recognition
```

## Testing

To test the API:

```bash
# Check health
curl http://localhost:8000/

# Register user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "test123"}'

# Login
curl -X POST http://localhost:8000/token \
  -F "username=test" \
  -F "password=test123"
```

## Production Deployment

1. Change `SECRET_KEY` to a secure random value
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS
4. Use a production WSGI server:

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints Summary

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login with password
- `POST /login/face` - Login with face
- `POST /register/face` - Register face

### User
- `GET /me` - Get current user
- `POST /character/select` - Select character

### Conversation
- `POST /conversation/start` - Start conversation
- `POST /conversation/{id}/end` - End and generate report
- `GET /conversation/{id}/report` - Get report
- `WS /ws/{conversation_id}` - WebSocket chat

## Dependencies

Core:
- fastapi - Web framework
- uvicorn - ASGI server
- sqlalchemy - ORM
- python-jose - JWT tokens
- passlib - Password hashing
- face-recognition - Facial authentication
- openai - GPT-4 chatbot

See `requirements.txt` for full list.
