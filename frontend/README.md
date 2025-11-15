# Homeless Assistant Frontend

React + TypeScript frontend for the Homeless Assistant chatbot application.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:3000

## Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## Features

### Authentication
- Password-based login/registration
- Facial recognition authentication
- Guest access (no registration)

### 3D Characters
- Interactive 3D character selection
- Built with React Three Fiber
- 4 unique assistant characters

### Chat Interface
- Real-time text chat
- Voice conversation mode
- Speech-to-text input
- Text-to-speech responses
- WebSocket communication

### Report Generation
- Generate detailed assistance reports
- Download as text file
- Share with service providers

## Browser Requirements

### Required Features
- WebSocket support
- ES6+ JavaScript
- Camera access (for facial recognition)

### Optional Features
- Web Speech API (for voice mode)
  - Chrome/Edge: Full support
  - Safari/Firefox: Limited support

## Configuration

### API Endpoint

Edit `src/api/client.ts` to change the backend URL:

```typescript
const API_BASE_URL = 'http://localhost:8000'
```

### Development Port

Edit `vite.config.ts` to change the dev server port:

```typescript
export default defineConfig({
  server: {
    port: 3000
  }
})
```

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client
│   │   └── client.ts
│   ├── pages/         # Page components
│   │   ├── Login.tsx
│   │   ├── CharacterSelect.tsx
│   │   └── Chat.tsx
│   ├── store/         # State management
│   │   └── authStore.ts
│   ├── styles/        # CSS files
│   │   ├── Login.css
│   │   ├── CharacterSelect.css
│   │   └── Chat.css
│   ├── App.tsx        # Main app component
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## State Management

Uses Zustand for lightweight state management:

```typescript
// Auth state
const { token, user, setToken, setUser, logout } = useAuthStore()
```

## Routing

React Router is used for navigation:

- `/login` - Login/registration page
- `/character-select` - Character selection (protected)
- `/chat` - Chat interface (protected)

## API Integration

### REST Endpoints

```typescript
import { api } from './api/client'

// Register
await api.register({ username, email, password })

// Login
const { access_token } = await api.login(username, password)

// Get current user
const user = await api.getMe()
```

### WebSocket

```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/${conversationId}`)

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle message
}

ws.send(JSON.stringify({ content: message, is_voice: false }))
```

## Voice Features

### Speech-to-Text

Uses Web Speech API (Chrome/Edge recommended):

```typescript
const recognition = new webkitSpeechRecognition()
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript
  // Send to chat
}
```

### Text-to-Speech

```typescript
const utterance = new SpeechSynthesisUtterance(text)
speechSynthesis.speak(utterance)
```

## Troubleshooting

### Camera Access Denied
- Check browser permissions
- Ensure HTTPS in production
- Allow camera access when prompted

### Voice Not Working
- Use Chrome or Edge browser
- Check microphone permissions
- Ensure HTTPS in production (required for getUserMedia)

### 3D Characters Not Rendering
- Check WebGL support: https://get.webgl.org/
- Update graphics drivers
- Try disabling browser extensions

### CORS Errors
- Ensure backend is running
- Check backend CORS configuration
- Verify API_BASE_URL is correct

## Dependencies

### Core
- react - UI framework
- react-dom - React DOM renderer
- react-router-dom - Routing
- typescript - Type safety

### 3D Graphics
- @react-three/fiber - React renderer for Three.js
- @react-three/drei - Helpers for R3F
- three - 3D graphics library

### State & API
- zustand - State management
- axios - HTTP client

See `package.json` for complete dependency list.

## Development Tips

### Hot Module Replacement

Vite provides fast HMR. Changes to React components will update instantly without full page reload.

### TypeScript

The project uses strict TypeScript. Enable editor TypeScript support for best experience:

- VS Code: Built-in
- WebStorm: Built-in
- Others: Install TypeScript language server

### Debugging

Use browser DevTools:
- React DevTools extension
- Network tab for API calls
- Console for errors
- Application tab for localStorage

## Performance

### Optimization Tips

1. The production build is automatically optimized
2. Code splitting happens automatically with dynamic imports
3. 3D scenes use React Three Fiber's optimizations
4. State updates are minimal with Zustand

### Bundle Size

Check bundle size:
```bash
npm run build
```

The dist/ folder size should be reasonable for a modern web app.

## Contributing

When adding new features:

1. Create new components in appropriate directories
2. Add TypeScript types for all props and state
3. Follow existing code style
4. Update this README if needed

## License

Part of the Homeless Assistant project to help individuals access support services.
