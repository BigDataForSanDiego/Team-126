# Homeless Assistant Chatbot - Setup Guide

A compassionate AI-powered chatbot solution designed to help homeless individuals access resources, support, and assistance.

## Features

- **Multiple Authentication Methods**
  - Username/Email and Password
  - Facial Recognition
  - Guest Access (no registration required)

- **3D Character Selection**
  - Choose from 4 friendly assistant characters
  - Interactive 3D previews

- **Real-time Communication**
  - Text chat interface
  - Voice conversation mode with speech-to-text and text-to-speech
  - Seamless switching between modes

- **AI-Powered Assistance**
  - Compassionate responses focused on homeless support
  - Information about shelters, food banks, healthcare, job training, etc.
  - Personalized guidance and action plans

- **Report Generation**
  - Detailed reports summarizing conversation and needs
  - Downloadable for sharing with social workers
  - Includes recommended resources and next steps

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **WebSocket** - Real-time communication
- **Google Vertex AI (Gemini)** - AI chatbot
- **Face Recognition** - Facial authentication
- **JWT** - Secure authentication

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **React Three Fiber** - 3D graphics
- **Zustand** - State management
- **Web Speech API** - Voice features

## Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **Google Cloud Account** with Vertex AI enabled
- **gcloud CLI** installed and configured

## Installation

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Authenticate with Google Cloud
gcloud auth application-default login

# Create .env file
cp .env.example .env

# Edit .env file and add your Google Cloud project
# Required: GOOGLE_CLOUD_PROJECT=your-project-id
# Optional: GOOGLE_CLOUD_LOCATION=us-central1
# Optional: Update SECRET_KEY for production
```

**For detailed Vertex AI setup, see [backend/VERTEX_AI_SETUP.md](backend/VERTEX_AI_SETUP.md)**

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend Server

```bash
# From backend directory with virtual environment activated
cd backend
python main.py

# Or using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
# From frontend directory
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage Guide

### 1. Login/Registration

**Option A: Password Authentication**
- Click "Register" to create a new account
- Enter username, email, and password
- Login with your credentials

**Option B: Facial Recognition**
- Click "Use Face Recognition"
- Allow camera access
- Capture your face for authentication
- On first use, you'll need to register with password first, then register your face

**Option C: Guest Access**
- Click "Continue as Guest"
- No registration required
- Note: Guest sessions are not persistent

### 2. Character Selection

- Browse 4 available assistant characters
- Click on a character to select
- Each character has a unique personality and appearance
- Click "Continue" to start chatting

### 3. Chat Interface

**Text Mode (Default)**
- Type your message in the input box
- Press Enter or click "Send"
- The AI assistant will respond with helpful information

**Voice Mode**
- Click "Voice On" to switch to voice mode
- Click "Hold to Speak" to record your voice
- The system will transcribe your speech and respond
- Responses will be spoken aloud automatically

**Generate Report**
- Click "Generate Report" at any time
- The AI will create a detailed summary including:
  - Your situation and needs
  - Resources discussed
  - Recommended next steps
  - Follow-up recommendations
- Download the report to share with social workers or service providers

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login with password
- `POST /login/face` - Login with facial recognition
- `POST /register/face` - Register face for existing user
- `GET /me` - Get current user info

### Character
- `POST /character/select` - Select 3D character

### Conversation
- `POST /conversation/start` - Start new conversation
- `POST /conversation/{id}/end` - End conversation and generate report
- `GET /conversation/{id}/report` - Get conversation report
- `WS /ws/{conversation_id}` - WebSocket for real-time chat

## Configuration

### Backend Environment Variables (.env)

```env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///./homeless_assistant.db
OPENAI_API_KEY=your-openai-api-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend API Configuration

Edit `frontend/src/api/client.ts` to change the backend URL:

```typescript
const API_BASE_URL = 'http://localhost:8000'
```

## Database

The application uses SQLite by default. The database file (`homeless_assistant.db`) will be created automatically in the backend directory on first run.

### Database Schema

- **users** - User accounts and authentication
- **conversations** - Chat sessions
- **messages** - Individual messages in conversations

## Browser Compatibility

### Required Features
- **WebSocket** - For real-time chat
- **getUserMedia** - For facial recognition
- **Web Speech API** - For voice features (optional)

### Recommended Browsers
- Google Chrome 90+
- Microsoft Edge 90+
- Safari 14+ (limited speech API support)
- Firefox 88+ (limited speech API support)

## Troubleshooting

### Backend Issues

**Database errors**
```bash
# Delete database and restart
rm homeless_assistant.db
python main.py
```

**Face recognition installation issues**
```bash
# On macOS, you may need:
brew install cmake

# On Linux, you may need:
sudo apt-get install cmake libopenblas-dev liblapack-dev
```

### Frontend Issues

**Port already in use**
```bash
# Change port in vite.config.ts or kill process using port 3000
```

**3D graphics not rendering**
- Check browser WebGL support
- Update graphics drivers
- Try a different browser

### API Issues

**CORS errors**
- Ensure backend CORS middleware includes frontend URL
- Check frontend is running on correct port (3000)

**Vertex AI errors**
- Verify you're authenticated: `gcloud auth application-default login`
- Check project ID is correct in .env
- Ensure Vertex AI API is enabled: `gcloud services enable aiplatform.googleapis.com`
- Verify billing is enabled on your Google Cloud project
- Check internet connection is stable

## Development

### Building for Production

**Backend**
```bash
# Backend runs the same way in production
# Consider using gunicorn or similar WSGI server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend**
```bash
cd frontend
npm run build
# Serve the dist/ folder with a web server
```

### Code Structure

**Backend**
- `main.py` - FastAPI application and routes
- `models.py` - Database models
- `auth.py` - Authentication logic
- `chatbot.py` - AI chatbot logic
- `database.py` - Database configuration

**Frontend**
- `src/App.tsx` - Main application component
- `src/pages/` - Page components
- `src/api/` - API client
- `src/store/` - State management
- `src/styles/` - CSS files

## Security Considerations

1. **Change SECRET_KEY** in production
2. **Use HTTPS** for facial recognition in production
3. **Validate and sanitize** all user inputs
4. **Rate limit** API endpoints
5. **Secure database** with proper backups
6. **Protect API keys** - never commit to version control

## License

This project is designed to help homeless individuals access resources and support services.

## Support

For issues, questions, or contributions, please open an issue on the project repository.

## Acknowledgments

- Google Cloud and Vertex AI for Gemini models
- Face Recognition library by Adam Geitgey
- React Three Fiber community
- FastAPI framework
