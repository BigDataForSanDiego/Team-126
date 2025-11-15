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
import { ResourceMap } from '../components/ResourceMap'
import '../styles/Chat.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

// Character configuration - switch between different character types here
const CHARACTER_CONFIG = {
  // Select character type: 'improved' | 'readyplayerme' | 'glb'
  type: 'readyplayerme' as 'improved' | 'readyplayerme' | 'glb',

  // Ready Player Me avatar URL (if using readyplayerme type)
  // Visit https://readyplayer.me/ to create and get URL
  readyPlayerMeUrl: 'https://models.readyplayer.me/6917b775672cca15c2f35e05.glb',

  // GLB model path (if using glb type)
  // Place .glb files in the frontend/public/models/ directory
  glbModelPath: '/models/character.glb',
}

// Simple Character component as a fallback
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
  const [report, setReport] = useState<string | null>(null)
  const [reportResources, setReportResources] = useState<any[]>([])
  const [showReport, setShowReport] = useState(false)
  const [isVoiceMode, setIsVoiceMode] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [resources, setResources] = useState<any[]>([])
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recognitionRef = useRef<any>(null)
  const recordingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const { user } = useAuthStore()

  const characterColor = user?.character_id
    ? ['#4a90e2', '#7b68ee', '#50c878', '#ff6b6b'][user.character_id - 1] || '#4a90e2'
    : '#4a90e2'

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition()
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = 'en-US'

        recognition.onstart = () => {
          console.log('[Speech] Recognition started')
          setIsRecording(true)
        }

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          const confidence = event.results[0][0].confidence

          console.log('========================================')
          console.log('[Speech Recognition] DETECTED TEXT:', transcript)
          console.log('[Speech Recognition] Confidence:', (confidence * 100).toFixed(1) + '%')
          console.log('========================================')

          // Clear timeout
          if (recordingTimeoutRef.current) {
            clearTimeout(recordingTimeoutRef.current)
            recordingTimeoutRef.current = null
          }

          setIsRecording(false)
          if (transcript) {
            sendMessage(transcript, true)
          }
        }

        recognition.onerror = (event: any) => {
          console.error('[Speech] Error:', event.error)

          // Clear timeout
          if (recordingTimeoutRef.current) {
            clearTimeout(recordingTimeoutRef.current)
            recordingTimeoutRef.current = null
          }

          setIsRecording(false)
        }

        recognition.onend = () => {
          console.log('[Speech] Recognition ended')

          // Clear timeout
          if (recordingTimeoutRef.current) {
            clearTimeout(recordingTimeoutRef.current)
            recordingTimeoutRef.current = null
          }

          setIsRecording(false)
        }

        recognitionRef.current = recognition
      } else {
        console.warn('[Speech] Speech recognition not supported')
      }
    }
  }, [])

  // Analyze audio for lip-sync animation
  const analyzeAudio = () => {
    if (!analyserRef.current) return

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
    analyserRef.current.getByteFrequencyData(dataArray)

    // Calculate average volume for lip-sync
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
    const normalizedLevel = Math.min(average / 128, 1)
    setAudioLevel(normalizedLevel)

    // Continue animation loop
    animationFrameRef.current = requestAnimationFrame(analyzeAudio)
  }

  // Text-to-speech function with lip-sync
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()

      setIsSpeaking(true)
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1.0
      utterance.pitch = 1.0
      utterance.volume = 1.0

      // Start lip-sync animation
      utterance.onstart = () => {
        // Start audio analysis for lip-sync (simplified version)
        // We'll use a simple mouth opening animation based on speaking state
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        // Simulate mouth movement with random values during speech
        const animateMouth = () => {
          if (!window.speechSynthesis.speaking) {
            setAudioLevel(0)
            return
          }
          setAudioLevel(0.3 + Math.random() * 0.4)
          animationFrameRef.current = requestAnimationFrame(animateMouth)
        }
        animateMouth()
      }

      utterance.onend = () => {
        setIsSpeaking(false)
        setAudioLevel(0)
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
      }

      utterance.onerror = () => {
        setIsSpeaking(false)
        setAudioLevel(0)
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
      }

      window.speechSynthesis.speak(utterance)
    }
  }

  // Start voice recording
  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      try {
        recognitionRef.current.start()

        // Set a safety timeout to auto-stop after 10 seconds
        recordingTimeoutRef.current = setTimeout(() => {
          console.log('[Speech] Auto-stopping after timeout')
          stopRecording()
        }, 10000)
      } catch (error) {
        console.error('[Speech] Failed to start:', error)
      }
    }
  }

  // Stop voice recording
  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      try {
        // Clear the timeout
        if (recordingTimeoutRef.current) {
          clearTimeout(recordingTimeoutRef.current)
          recordingTimeoutRef.current = null
        }

        recognitionRef.current.stop()
        setIsRecording(false)
        console.log('[Speech] Manually stopped recording')
      } catch (error) {
        console.error('[Speech] Failed to stop:', error)
      }
    }
  }

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
          console.log('[WS] Received content:', content)

          try {
            const parsedContent = JSON.parse(content)
            console.log('[WS] Parsed JSON:', parsedContent)

            if (parsedContent.type === 'request_location') {
              console.log('[WS] Location request detected!')

              // DO NOT display the location request message - handle it silently in the background

              // Automatically get location
              console.log('[Location] Requesting location from browser...')
              const location = await getCurrentLocation()
              console.log('[Location] Result:', location)

              if (location.error) {
                // Send error message
                console.error('[Location] Error:', location.error)
                const errorMsg = `I'm unable to access your location: ${location.error}. You can manually tell me your city or address instead.`
                const errorMessage: Message = {
                  role: 'user',
                  content: errorMsg,
                  timestamp: new Date().toISOString()
                }
                setMessages(prev => [...prev, errorMessage])
                websocket.send(JSON.stringify({ content: errorMsg, is_voice: false }))
              } else if (location.latitude && location.longitude) {
                // Save user location for map
                setUserLocation({
                  latitude: location.latitude,
                  longitude: location.longitude
                })

                // Send location back to assistant silently (don't add to messages array)
                console.log('[Location] Sending coordinates to assistant')
                const locationMsg = `My current location is: Latitude ${location.latitude.toFixed(6)}, Longitude ${location.longitude.toFixed(6)}.`
                // DO NOT add locationMessage to messages array - keep it in the background
                websocket.send(JSON.stringify({ content: locationMsg, is_voice: false }))
              }
              return
            }
          } catch (e) {
            // Not a JSON string, continue with normal message handling
            console.log('[WS] Not JSON or parse failed:', e)
          }

          // Parse resource data if present
          let displayContent = content
          console.log('[Resources] Checking message for resource data...')
          const resourceMatch = content.match(/<!-- RESOURCE_DATA:(.+?) -->/s)
          if (resourceMatch) {
            console.log('[Resources] Found resource data marker')
            try {
              const resourceData = JSON.parse(resourceMatch[1])
              console.log('[Resources] Parsed resource data:', resourceData)
              if (resourceData.type === 'resource_list' && resourceData.resources) {
                setResources(resourceData.resources)
                console.log('[Resources] Set', resourceData.resources.length, 'resources to state')
              }
              // Remove the resource data comment from display
              displayContent = content.replace(/<!-- RESOURCE_DATA:.+? -->/s, '')
            } catch (e) {
              console.error('[Resources] Failed to parse resource data:', e)
              console.error('[Resources] Raw match:', resourceMatch[1])
            }
          } else {
            console.log('[Resources] No resource data found in message')
          }

          const newMessage: Message = {
            role: data.role,
            content: displayContent,
            timestamp: data.timestamp
          }
          setMessages(prev => [...prev, newMessage])

          // Speak the response if in voice mode
          if (isVoiceMode && data.role === 'assistant') {
            speakText(displayContent)
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

    return () => {
      if (ws) {
        ws.close()
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

  const generateReport = async () => {
    if (!conversationId) return

    try {
      const data = await api.endConversation(conversationId)

      // Parse resource data from report if present
      console.log('[Report] Checking for resource data...')
      const resourceMatch = data.report.match(/<!-- RESOURCE_DATA:(.+?) -->/s)
      if (resourceMatch) {
        console.log('[Report] Found resource data marker')
        try {
          const resourceData = JSON.parse(resourceMatch[1])
          console.log('[Report] Parsed resource data:', resourceData)
          if (resourceData.type === 'resource_list' && resourceData.resources) {
            setReportResources(resourceData.resources)
            console.log('[Report] Set', resourceData.resources.length, 'resources to state')
          }
          // Remove resource marker from displayed report
          setReport(data.report.replace(/<!-- RESOURCE_DATA:.+? -->/s, ''))
        } catch (e) {
          console.error('[Report] Failed to parse resource data:', e)
          setReport(data.report)
        }
      } else {
        console.log('[Report] No resource data found')
        setReport(data.report)
      }

      setShowReport(true)
    } catch (err) {
      console.error('Error generating report:', err)
    }
  }

  const printReport = () => {
    if (!report) return

    // Create a new window for printing
    const printWindow = window.open('', '_blank')
    if (!printWindow) return

    // Create HTML content with proper styling
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Assistance Report</title>
          <style>
            @media print {
              @page {
                margin: 1in;
              }
            }
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
              line-height: 1.6;
              color: #333;
              max-width: 800px;
              margin: 0 auto;
              padding: 20px;
            }
            h1, h2, h3, h4, h5, h6 {
              color: #2c3e50;
              margin-top: 24px;
              margin-bottom: 12px;
            }
            h1 { font-size: 2em; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px; }
            h3 { font-size: 1.25em; }
            p { margin: 12px 0; }
            ul, ol {
              margin: 12px 0;
              padding-left: 30px;
            }
            li { margin: 6px 0; }
            strong { color: #2c3e50; }
            code {
              background: #f5f5f5;
              padding: 2px 6px;
              border-radius: 3px;
              font-family: 'Courier New', monospace;
              font-size: 0.9em;
            }
            pre {
              background: #f5f5f5;
              padding: 15px;
              border-radius: 5px;
              overflow-x: auto;
            }
            pre code {
              background: none;
              padding: 0;
            }
            blockquote {
              border-left: 4px solid #3b82f6;
              margin: 12px 0;
              padding-left: 15px;
              color: #666;
            }
            table {
              border-collapse: collapse;
              width: 100%;
              margin: 15px 0;
            }
            th, td {
              border: 1px solid #ddd;
              padding: 8px;
              text-align: left;
            }
            th {
              background-color: #f5f5f5;
              font-weight: 600;
            }
            .print-header {
              text-align: center;
              margin-bottom: 30px;
              padding-bottom: 20px;
              border-bottom: 3px solid #3b82f6;
            }
            .print-footer {
              margin-top: 40px;
              padding-top: 20px;
              border-top: 1px solid #e0e0e0;
              text-align: center;
              font-size: 0.9em;
              color: #666;
            }
          </style>
        </head>
        <body>
          <div class="print-header">
            <h1>Homeless Assistance Report</h1>
            <p>Generated on ${new Date().toLocaleString()}</p>
          </div>
          <div class="report-content">
            ${report.split('\n').map(line => {
              // Simple markdown parsing
              line = line.trim()
              if (line.startsWith('# ')) return `<h1>${line.substring(2)}</h1>`
              if (line.startsWith('## ')) return `<h2>${line.substring(3)}</h2>`
              if (line.startsWith('### ')) return `<h3>${line.substring(4)}</h3>`
              if (line.startsWith('- ')) return `<li>${line.substring(2)}</li>`
              if (line.startsWith('* ')) return `<li>${line.substring(2)}</li>`
              if (line.startsWith('**') && line.endsWith('**')) return `<p><strong>${line.substring(2, line.length - 2)}</strong></p>`
              if (line === '') return '<br>'
              return `<p>${line}</p>`
            }).join('\n')}
          </div>
          <div class="print-footer">
            <p>Report ID: ${conversationId}</p>
          </div>
          <script>
            window.onload = () => {
              window.print()
            }
          </script>
        </body>
      </html>
    `

    printWindow.document.write(htmlContent)
    printWindow.document.close()
  }

  return (
    <div className={`chat-container ${isVoiceMode ? 'voice-mode-layout' : ''}`}>
      {/* Character Display */}
      <div className={`character-display ${isVoiceMode ? 'voice-mode-character' : ''}`}>
        <Canvas camera={{ position: [0, 0.8, 3.5], fov: 50 }}>
          {/* Enhanced lighting to correctly display Ready Player Me character colors */}
          <ambientLight intensity={1.5} />
          <directionalLight position={[5, 5, 5]} intensity={2.0} castShadow />
          <directionalLight position={[-5, 3, -5]} intensity={1.0} />
          <pointLight position={[0, 2, 4]} intensity={1.2} color="#ffffff" />
          <hemisphereLight args={['#ffffff', '#8888ff', 0.8]} />

          {/* Render different types of characters based on configuration */}
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
              audioLevel={audioLevel}
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

      {/* Chat Interface - Hidden in Voice Mode */}
      {!isVoiceMode && (
        <div className="chat-interface">
          <div className="chat-header">
            <h2>How can I help you today?</h2>
            <div className="chat-controls">
              <button
                onClick={() => setIsVoiceMode(!isVoiceMode)}
                className={`control-btn ${isVoiceMode ? 'active' : ''}`}
              >
                {isVoiceMode ? 'Voice Mode' : 'Text Mode'}
              </button>
              <button onClick={generateReport} className="control-btn report-btn">
                Generate Report
              </button>
            </div>
          </div>

          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-content">
                  <strong>{msg.role === 'user' ? 'You' : 'Assistant'}</strong>
                  <div className="markdown-content">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}

            {/* Display map if resources are found */}
            {resources.length > 0 && (
              <div style={{ margin: '20px 30px' }}>
                <ResourceMap resources={resources} userLocation={userLocation || undefined} />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
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
          </div>
        </div>
      )}

      {/* Voice Mode Controls */}
      {isVoiceMode && (
        <div className="voice-mode-controls">
          <button
            onClick={() => setIsVoiceMode(false)}
            className="exit-voice-btn"
          >
            Exit Voice Mode
          </button>
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`voice-btn ${isRecording ? 'recording' : ''}`}
          >
            {isRecording ? 'Stop Recording' : 'Click to Speak'}
          </button>
        </div>
      )}

      {/* Report Modal */}
      {showReport && (
        <div className="modal-overlay" onClick={() => setShowReport(false)}>
          <div className="modal-content report-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Assistance Report</h2>
            <div className="markdown-report">
              <ReactMarkdown
                components={{
                  code: ({ node, inline, className, children, ...props }: any) =>
                    inline ? (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    ) : (
                      <pre>
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    )
                }}
              >
                {report || ''}
              </ReactMarkdown>

              {/* Display map if resources are included in the report */}
              {reportResources.length > 0 && (
                <div style={{ marginTop: '30px' }}>
                  <h3>Resource Locations Map</h3>
                  <ResourceMap resources={reportResources} userLocation={userLocation || undefined} />
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button onClick={printReport} className="btn-primary">
                Print / Save as PDF
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
