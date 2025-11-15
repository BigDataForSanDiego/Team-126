import { useGLTF } from '@react-three/drei'

interface ReadyPlayerMeCharacterProps {
  avatarUrl: string
  isSpeaking?: boolean
}

/**
 * Ready Player Me 3D Avatar Component
 *
 * 使用方法：
 * 1. 访问 https://readyplayer.me/ 创建免费头像
 * 2. 获取 .glb 文件URL
 * 3. 传入 avatarUrl prop
 */
export function ReadyPlayerMeCharacter({
  avatarUrl,
  isSpeaking = false
}: ReadyPlayerMeCharacterProps) {
  const { scene } = useGLTF(avatarUrl)

  return (
    <group scale={1.2} position={[0, -0.8, 0]}>
      <primitive object={scene} />
    </group>
  )
}
