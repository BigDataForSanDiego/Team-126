import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuthStore } from '../store/authStore'
import '../styles/Login.css'

function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [useFaceAuth, setUseFaceAuth] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const navigate = useNavigate()
  const { setToken, setUser } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        const data = await api.login(username || email, password)
        setToken(data.access_token)
        const userData = await api.getMe()
        setUser(userData)
        navigate('/character-select')
      } else {
        // Backend now returns both user and access_token
        const response = await api.register({ username, email, password })
        setToken(response.access_token)
        setUser(response.user)
        navigate('/character-select')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleGuestLogin = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await api.register({ is_guest: true })
      // Backend now returns both user and access_token
      setToken(response.access_token)
      setUser(response.user)
      navigate('/character-select')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setUseFaceAuth(true)
    } catch (err) {
      setError('Could not access camera')
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setUseFaceAuth(false)
  }

  const captureFace = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const canvas = canvasRef.current
    const video = videoRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx?.drawImage(video, 0, 0)

    canvas.toBlob(async (blob) => {
      if (!blob) return

      const file = new File([blob], 'face.jpg', { type: 'image/jpeg' })
      setLoading(true)

      try {
        if (isLogin) {
          const data = await api.loginFace(file)
          setToken(data.access_token)
          const userData = await api.getMe()
          setUser(userData)
          navigate('/character-select')
        } else {
          // For registration, we need to create account first
          const userData = await api.register({ username, email, password })
          const loginData = await api.login(username || email, password)
          setToken(loginData.access_token)
          setUser(userData)

          // Then register face
          await api.registerFace(file)
          navigate('/character-select')
        }
        stopCamera()
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Face authentication failed')
      } finally {
        setLoading(false)
      }
    }, 'image/jpeg')
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Welcome to Good Talks</h1>
        <p className="subtitle">Your AI companion for assistance and support</p>

        {error && <div className="error-message">{error}</div>}

        {!useFaceAuth ? (
          <form onSubmit={handleSubmit}>
            {!isLogin && (
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            )}
            <input
              type={isLogin ? 'text' : 'email'}
              placeholder={isLogin ? 'Username or Email' : 'Email'}
              value={isLogin ? username : email}
              onChange={(e) => isLogin ? setUsername(e.target.value) : setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Loading...' : isLogin ? 'Login' : 'Register'}
            </button>

            <div className="divider">OR</div>

            <button type="button" onClick={startCamera} className="btn-secondary">
              Use Face Recognition
            </button>

            <button type="button" onClick={handleGuestLogin} className="btn-secondary" disabled={loading}>
              Continue as Guest
            </button>

            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="btn-link"
            >
              {isLogin ? "Don't have an account? Register" : 'Already have an account? Login'}
            </button>
          </form>
        ) : (
          <div className="face-auth">
            <video ref={videoRef} autoPlay playsInline className="video-preview" />
            <canvas ref={canvasRef} style={{ display: 'none' }} />

            <div className="face-auth-buttons">
              <button onClick={captureFace} disabled={loading} className="btn-primary">
                {loading ? 'Processing...' : 'Capture Face'}
              </button>
              <button onClick={stopCamera} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Login
