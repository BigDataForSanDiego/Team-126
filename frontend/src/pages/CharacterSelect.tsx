import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { api } from '../api/client'
import { useAuthStore } from '../store/authStore'
import { ImprovedCharacter } from '../components/ImprovedCharacter'
import { ReadyPlayerMeCharacter } from '../components/ReadyPlayerMeCharacter'
import '../styles/CharacterSelect.css'

// 🎨 角色类型配置
const USE_READY_PLAYER_ME = true  // 设置为true使用Ready Player Me角色

// 🎭 通用角色配置
const characters = [
  {
    id: 1,
    color: '#7b68ee',
    emotion: 'happy' as const,
    rpmUrl: 'https://models.readyplayer.me/691796d0fb99478e419e02f8.glb'
  },
  {
    id: 2,
    color: '#50c878',
    emotion: 'happy' as const,
    rpmUrl: 'https://models.readyplayer.me/6917b775672cca15c2f35e05.glb'
  },
]

// 简单的Character组件作为降级方案
function Character({ color }: { color: string }) {
  return (
    <group>
      {/* Head */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Body */}
      <mesh position={[0, 0.8, 0]}>
        <cylinderGeometry args={[0.3, 0.4, 1, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Arms */}
      <mesh position={[-0.5, 0.8, 0]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 0.1, 0.8, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0.5, 0.8, 0]} rotation={[0, 0, -Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 0.1, 0.8, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      {/* Legs */}
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

function CharacterSelect() {
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const handleSelect = async () => {
    if (!selectedId || !user) return

    setLoading(true)
    setError('')
    try {
      await api.selectCharacter(selectedId, user.id)
      navigate('/chat')
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to select character'
      setError(errorMessage)
      console.error('Error selecting character:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="character-select-container">
      <div className="character-select-content">
        <h1>Choose Your Assistant</h1>
        <p className="subtitle">Select a character to help you</p>

        {error && <div className="error-message">{error}</div>}

        <div className="character-grid">
          {characters.map((character) => (
            <div
              key={character.id}
              className={`character-card ${selectedId === character.id ? 'selected' : ''}`}
              onClick={() => setSelectedId(character.id)}
            >
              <div className="character-preview">
                <Canvas camera={{ position: [0, 0.8, 3.5], fov: 50 }}>
                  {/* 增强光照以显示颜色 */}
                  <ambientLight intensity={1.2} />
                  <directionalLight position={[5, 5, 5]} intensity={1.5} castShadow />
                  <directionalLight position={[-5, 3, -5]} intensity={0.8} />
                  <pointLight position={[0, 2, 3]} intensity={1.0} color="#ffffff" />
                  <hemisphereLight args={['#ffffff', '#8888ff', 0.6]} />

                  {/* 根据配置使用Ready Player Me或改进的角色 */}
                  {USE_READY_PLAYER_ME ? (
                    <ReadyPlayerMeCharacter
                      avatarUrl={character.rpmUrl}
                      isSpeaking={false}
                    />
                  ) : (
                    <ImprovedCharacter
                      color={character.color}
                      emotion={character.emotion}
                      isSpeaking={false}
                    />
                  )}

                  <OrbitControls
                    enableZoom={false}
                    enablePan={false}
                    autoRotate={selectedId === character.id}
                    autoRotateSpeed={1.5}
                  />
                </Canvas>
              </div>
            </div>
          ))}
        </div>

        {selectedId && (
          <button onClick={handleSelect} disabled={loading} className="btn-continue">
            {loading ? 'Loading...' : 'Continue'}
          </button>
        )}
      </div>
    </div>
  )
}

export default CharacterSelect
