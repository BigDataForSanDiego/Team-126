# Homeless Assistant Chatbot - Project Implementation

A compassionate AI-powered chatbot solution designed to help homeless individuals access resources, mental health support, and assistance while collecting anonymized data to inform policy decisions.

## Overview

This project addresses two core themes from the 2025 Big Data Hackathon:
1. **Health and Mental Wellness Support** - Providing remote mental health care through an AI chatbot
2. **Data-Driven Policy and User-Centered Resource Planning** - Collecting anonymized data to inform policy

## Key Features

### Authentication & Accessibility
- **Password Login**: Traditional username/email and password authentication
- **Facial Recognition**: Secure biometric authentication using face recognition
- **Guest Access**: No registration required - anyone can get help immediately
- **Privacy-First**: Guest mode ensures privacy for those who need anonymity

### Interactive Experience
- **3D Character Selection**: Choose from 4 friendly AI assistant characters
  - Friendly Helper
  - Caring Guide
  - Wise Companion
  - Kind Assistant
- **Interactive 3D Preview**: See your assistant in 3D before selecting

### Communication Modes
- **Text Chat**: Traditional text-based conversation
- **Voice Mode**: Hands-free voice interaction
  - Speech-to-text for user input
  - Text-to-speech for assistant responses
- **Real-time Communication**: WebSocket-based instant messaging
- **Seamless Switching**: Toggle between text and voice modes anytime

### AI-Powered Assistance
- **Compassionate Responses**: Trained to be empathetic and non-judgmental
- **Resource Information**: Provides information about:
  - Emergency shelters and temporary housing
  - Food banks and meal programs
  - Healthcare services (including mental health)
  - Job training and employment assistance
  - Legal aid and advocacy services
  - Substance abuse treatment programs
  - Social services and benefits eligibility
- **Personalized Guidance**: Creates action plans based on individual needs
- **Crisis Support**: Encourages emergency services contact when needed

### Report Generation
- **Detailed Reports**: Generate comprehensive summaries including:
  - Summary of the person's situation
  - Identified needs and concerns
  - Resources and assistance discussed
  - Recommended next steps and action items
  - Follow-up recommendations
- **Downloadable**: Reports can be downloaded as text files
- **Shareable**: Can be shared with social workers and service providers
- **Professional Format**: Formatted for professional use

### Data Collection (Future Enhancement)
- Anonymized data on needs and challenges
- Trend analysis for policy makers
- Resource gap identification
- Service optimization insights

## Technology Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Python 3.8+** - Programming language
- **SQLAlchemy** - SQL toolkit and ORM
- **WebSocket** - Real-time bidirectional communication
- **OpenAI GPT-4** - Advanced AI for natural conversations
- **Face Recognition** - Facial authentication library
- **JWT** - Secure token-based authentication
- **SQLite/PostgreSQL** - Database storage

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **React Three Fiber** - 3D graphics with Three.js
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **Web Speech API** - Browser-based voice features

## Project Structure

```
Team-126/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application & routes
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication logic
│   ├── chatbot.py          # AI chatbot logic
│   ├── database.py         # Database configuration
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment template
│   └── README.md           # Backend docs
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   │   ├── Login.tsx           # Login/register page
│   │   │   ├── CharacterSelect.tsx # Character selection
│   │   │   └── Chat.tsx            # Chat interface
│   │   ├── api/           # API client
│   │   │   └── client.ts  # API functions
│   │   ├── store/         # State management
│   │   │   └── authStore.ts
│   │   ├── styles/        # CSS files
│   │   ├── App.tsx        # Main component
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Dependencies
│   ├── tsconfig.json      # TypeScript config
│   └── README.md          # Frontend docs
│
├── SETUP.md               # Complete setup guide
├── README.md              # Hackathon proposal
└── PROJECT_README.md      # This file
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Google Cloud account with Vertex AI enabled
- gcloud CLI installed

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Team-126
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
gcloud auth application-default login
cp .env.example .env
# Edit .env and add your GOOGLE_CLOUD_PROJECT
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

1. **Start Backend** (from backend directory)
```bash
python main.py
```
Backend runs at: `http://localhost:8000`

2. **Start Frontend** (from frontend directory)
```bash
npm run dev
```
Frontend runs at: `http://localhost:3000`

3. **Access Application**
- Open browser to `http://localhost:3000`
- Choose authentication method (password, face, or guest)
- Select your 3D character assistant
- Start chatting!

## Usage Guide

### For Homeless Individuals

1. **Getting Started**
   - Visit the kiosk/website
   - Choose "Continue as Guest" for privacy
   - Or create an account for persistent history

2. **Selecting Your Assistant**
   - Browse the 4 available characters
   - Choose one that feels comfortable to you
   - Click continue to start

3. **Getting Help**
   - Type or speak your concerns
   - Be as specific as possible about your needs
   - Ask about shelters, food, healthcare, jobs, etc.

4. **Getting a Report**
   - Click "Generate Report" when ready
   - Download the report
   - Share with social workers if desired

### For Social Workers

1. **Understanding Reports**
   - Reports summarize the individual's situation
   - Include identified needs and resources discussed
   - Provide recommended next steps
   - Can inform case management

2. **Using the Data**
   - Reports help understand individual needs
   - Track common challenges across conversations
   - Identify resource gaps in the community
   - Inform service planning and policy

## API Documentation

### Endpoints

#### Authentication
- `POST /register` - Register new user
- `POST /token` - Login with password
- `POST /login/face` - Login with facial recognition
- `POST /register/face` - Register face for user
- `GET /me` - Get current user info

#### Character & Conversation
- `POST /character/select` - Select 3D character
- `POST /conversation/start` - Start new conversation
- `POST /conversation/{id}/end` - End and generate report
- `GET /conversation/{id}/report` - Get conversation report
- `WS /ws/{conversation_id}` - WebSocket for real-time chat

Full API documentation available at `http://localhost:8000/docs` when backend is running.

## Security & Privacy

- **Guest Mode**: Complete anonymity for those who need it
- **Encrypted Storage**: Passwords are hashed with bcrypt
- **JWT Tokens**: Secure authentication tokens
- **Face Data**: Encrypted and securely stored
- **HTTPS Ready**: Production deployment uses HTTPS
- **Data Anonymization**: Reports can be anonymized for research

## Future Enhancements

- **Multilingual Support**: Support for Spanish and other languages
- **SMS Integration**: Text-based access without internet
- **Location Services**: Show nearby resources on a map
- **Follow-up Scheduling**: Reminder system for appointments
- **Data Dashboard**: Analytics for policy makers
- **Mobile App**: Native iOS and Android apps
- **Offline Mode**: Basic functionality without internet
- **Integration**: Connect with existing social service systems

## Browser Compatibility

### Recommended Browsers
- Google Chrome 90+ (best experience)
- Microsoft Edge 90+
- Safari 14+ (limited voice features)
- Firefox 88+ (limited voice features)

### Required Features
- WebSocket support
- Camera access (for facial recognition)
- Microphone access (for voice mode)
- WebGL (for 3D characters)

## Deployment

### Development
Currently configured for local development.

### Production (Future)
- Deploy backend to cloud service (AWS, Google Cloud, Azure)
- Deploy frontend to static hosting (Vercel, Netlify, S3)
- Use PostgreSQL for production database
- Enable HTTPS with SSL certificates
- Set up monitoring and logging
- Configure rate limiting and security

## Contributing

This project is designed to help homeless individuals. Contributions should:
- Maintain compassionate, non-judgmental tone
- Prioritize accessibility and ease of use
- Protect user privacy and dignity
- Support the core mission of helping those in need

## License

This project was created for the 2025 Big Data Hackathon to address homelessness challenges in San Diego.

## Acknowledgments

- **Google Cloud** for Vertex AI and Gemini models enabling compassionate AI conversations
- **Adam Geitgey** for the face_recognition library
- **FastAPI** team for the excellent web framework
- **React Three Fiber** community for 3D graphics tools
- **Big Data for San Diego** for organizing the hackathon
- **San Diego Homeless Community** for inspiring this solution

## Contact & Support

For questions, issues, or contributions related to this project, please contact the team through GitHub.

## Impact

This chatbot aims to:
- Provide 24/7 accessible mental health and resource support
- Reduce barriers to accessing help (no stigma, no appointments needed)
- Collect data to inform better policies and resource allocation
- Connect individuals with appropriate services faster
- Improve outcomes for homeless individuals in San Diego

---

**Together, we can make a difference in the lives of those experiencing homelessness.**
