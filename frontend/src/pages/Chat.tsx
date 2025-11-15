import { useState, useEffect, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { api, API_BASE_URL } from '../api/client'
import { useAuthStore } from '../store/authStore'
import { ImprovedCharacter } from '../components/ImprovedCharacter'
import { ReadyPlayerMeCharacter } from '../components/ReadyPlayerMeCharacter'
import { GLBCharacter } from '../components/GLBCharacter'
import { getCurrentLocation } from '../hooks/useGeolocation'
import ReactMarkdown from 'react-markdown'
import '../styles/Chat.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

// 🎨 角色配置 - 在这里切换不同的角色类型
const CHARACTER_CONFIG = {
  // 选择角色类型：'improved' | 'readyplayerme' | 'glb'
  type: 'readyplayerme' as 'improved' | 'readyplayerme' | 'glb',

  // Ready Player Me 头像URL（如果使用readyplayerme类型）
  // 访问 https://readyplayer.me/ 创建并获取URL
  readyPlayerMeUrl: 'https://models.readyplayer.me/6917b775672cca15c2f35e05.glb',

  // GLB模型路径（如果使用glb类型）
  // 将.glb文件放到 frontend/public/models/ 目录
  glbModelPath: '/models/character.glb',
}

// 简单的Character组件作为降级方案
function Character({ color }: { color: string }) {
  return (
    <group>
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.8, 0]}>
        <cylinderGeometry args={[0.3, 0.4, 1, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[-0.5, 0.8, 0]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 0.1, 0.8, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0.5, 0.8, 0]} rotation={[0, 0, -Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 0.1, 0.8, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[-0.2, 0, 0]}>
        <cylinderGeometry args={[0.12, 0.12, 0.6, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0.2, 0, 0]}>
        <cylinderGeometry args={[0.12, 0.12, 0.6, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  )
}

function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [isVoiceMode, setIsVoiceMode] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [report, setReport] = useState<string | null>(null)
  const [showReport, setShowReport] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const { user } = useAuthStore()

  const characterColor = user?.character_id
    ? ['#4a90e2', '#7b68ee', '#50c878', '#ff6b6b'][user.character_id - 1] || '#4a90e2'
    : '#4a90e2'

  useEffect(() => {
    // Initialize conversation
    const initConversation = async () => {
      if (!user) return

      try {
        const data = await api.startConversation(user.id)
        setConversationId(data.conversation_id)

        // Connect WebSocket
        const token = localStorage.getItem('auth-storage')
        const websocket = new WebSocket(`ws://localhost:8000/ws/${data.conversation_id}`)

        websocket.onopen = () => {
          console.log('WebSocket connected')
        }

        websocket.onmessage = async (event) => {
          const data = JSON.parse(event.data)
          if (data.error) {
            console.error('WebSocket error:', data.error)
            return
          }

          // Check if the response is a JSON string with location request
          let content = data.content
          try {
            const parsedContent = JSON.parse(content)
            if (parsedContent.type === 'request_location') {
              // Display the message asking for permission
              const requestMessage: Message = {
                role: 'assistant',
                content: parsedContent.message,
                timestamp: data.timestamp
              }
              setMessages(prev => [...prev, requestMessage])

              // Automatically get location
              const location = await getCurrentLocation()

              if (location.error) {
                // Send error message
                const errorMsg = `I'm unable to access your location: ${location.error}. You can manually tell me your city or address instead.`
                const errorMessage: Message = {
                  role: 'user',
                  content: errorMsg,
                  timestamp: new Date().toISOString()
                }
                setMessages(prev => [...prev, errorMessage])
                websocket.send(JSON.stringify({ content: errorMsg, is_voice: false }))
              } else if (location.latitude && location.longitude) {
                // Send location back to assistant
                const locationMsg = `My current location is: Latitude ${location.latitude.toFixed(6)}, Longitude ${location.longitude.toFixed(6)}.`
                const locationMessage: Message = {
                  role: 'user',
                  content: locationMsg,
                  timestamp: new Date().toISOString()
                }
                setMessages(prev => [...prev, locationMessage])
                websocket.send(JSON.stringify({ content: locationMsg, is_voice: false }))
              }
              return
            }
          } catch {
            // Not a JSON string, continue with normal message handling
          }

          const newMessage: Message = {
            role: data.role,
            content: content,
            timestamp: data.timestamp
          }
          setMessages(prev => [...prev, newMessage])

          // Speak response if in voice mode
          if (isVoiceMode) {
            speakText(content)
          }
        }

        websocket.onerror = (error) => {
          console.error('WebSocket error:', error)
        }

        setWs(websocket)
      } catch (err) {
        console.error('Error starting conversation:', err)
      }
    }

    initConversation()

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        sendMessage(transcript, true)
        setIsRecording(false)
      }

      recognitionRef.current.onerror = () => {
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }

    return () => {
      if (ws) {
        ws.close()
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [user])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = (content: string, isVoice: boolean = false) => {
    if (!content.trim() || !ws) return

    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    ws.send(JSON.stringify({ content, is_voice: isVoice }))
    setInputMessage('')
  }

  const handleSendMessage = () => {
    sendMessage(inputMessage)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const toggleVoiceMode = () => {
    setIsVoiceMode(!isVoiceMode)
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setIsRecording(true)
      recognitionRef.current.start()
    }
  }

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
    }
  }

  const generateReport = async () => {
    if (!conversationId) return

    try {
      const data = await api.endConversation(conversationId)
      setReport(data.report)
      setShowReport(true)
    } catch (err) {
      console.error('Error generating report:', err)
    }
  }

  const downloadReport = () => {
    if (!report) return

    const blob = new Blob([report], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assistance-report-${conversationId}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="chat-container">
      {/* Character Display */}
      <div className="character-display">
        <Canvas camera={{ position: [0, 0.8, 3.5], fov: 50 }}>
          {/* 增强光照以正确显示Ready Player Me角色颜色 */}
          <ambientLight intensity={1.5} />
          <directionalLight position={[5, 5, 5]} intensity={2.0} castShadow />
          <directionalLight position={[-5, 3, -5]} intensity={1.0} />
          <pointLight position={[0, 2, 4]} intensity={1.2} color="#ffffff" />
          <hemisphereLight args={['#ffffff', '#8888ff', 0.8]} />

          {/* 根据配置渲染不同类型的角色 */}
          {CHARACTER_CONFIG.type === 'improved' && (
            <ImprovedCharacter
              color={characterColor}
              isSpeaking={isSpeaking}
              emotion="happy"
            />
          )}

          {CHARACTER_CONFIG.type === 'readyplayerme' && (
            <ReadyPlayerMeCharacter
              avatarUrl={CHARACTER_CONFIG.readyPlayerMeUrl}
              isSpeaking={isSpeaking}
            />
          )}

          {CHARACTER_CONFIG.type === 'glb' && (
            <GLBCharacter
              modelPath={CHARACTER_CONFIG.glbModelPath}
              isSpeaking={isSpeaking}
              animationName="idle"
            />
          )}

          <OrbitControls
            enableZoom={false}
            enablePan={false}
            autoRotate={true}
            autoRotateSpeed={0.5}
          />
        </Canvas>
      </div>

      {/* Chat Interface */}
      <div className="chat-interface">
        <div className="chat-header">
          <h2>How can I help you today?</h2>
          <div className="chat-controls">
            <button
              onClick={toggleVoiceMode}
              className={`control-btn ${isVoiceMode ? 'active' : ''}`}
            >
              {isVoiceMode ? '🔊 Voice On' : '💬 Text Mode'}
            </button>
            <button onClick={generateReport} className="control-btn report-btn">
              📄 Generate Report
            </button>
          </div>
        </div>

        <div className="messages-container">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong>
                <div className="markdown-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          {isVoiceMode ? (
            <button
              onClick={startRecording}
              disabled={isRecording}
              className={`voice-btn ${isRecording ? 'recording' : ''}`}
            >
              {isRecording ? '🎤 Recording...' : '🎤 Hold to Speak'}
            </button>
          ) : (
            <>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="message-input"
              />
              <button onClick={handleSendMessage} className="send-btn">
                Send
              </button>
            </>
          )}
        </div>
      </div>

      {/* Report Modal */}
      {showReport && (
        <div className="modal-overlay" onClick={() => setShowReport(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Assistance Report</h2>
            <div className="report-content">
              {report}
            </div>
            <div className="modal-actions">
              <button onClick={downloadReport} className="btn-primary">
                Download Report
              </button>
              <button onClick={() => setShowReport(false)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Chat
