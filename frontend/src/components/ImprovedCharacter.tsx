import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface ImprovedCharacterProps {
  color: string
  isSpeaking?: boolean
  emotion?: 'happy' | 'neutral' | 'thinking'
}

/**
 * 改进的3D拟人角色组件
 * 特点：
 * - 更拟人化的比例
 * - 面部表情（眼睛、嘴巴）
 * - 说话时的动画
 * - 呼吸效果
 */
export function ImprovedCharacter({
  color,
  isSpeaking = false,
  emotion = 'neutral'
}: ImprovedCharacterProps) {
  const groupRef = useRef<THREE.Group>(null)
  const headRef = useRef<THREE.Mesh>(null)
  const leftEyeRef = useRef<THREE.Mesh>(null)
  const rightEyeRef = useRef<THREE.Mesh>(null)
  const mouthRef = useRef<THREE.Mesh>(null)

  // 动画逻辑
  useFrame((state) => {
    if (!groupRef.current) return

    const time = state.clock.getElapsedTime()

    // 整体轻微摇摆（呼吸效果）
    groupRef.current.position.y = Math.sin(time * 1.5) * 0.05

    // 头部说话时的动画
    if (isSpeaking && headRef.current) {
      headRef.current.rotation.x = Math.sin(time * 10) * 0.05

      // 嘴巴张合
      if (mouthRef.current) {
        const mouthScale = 1 + Math.abs(Math.sin(time * 12)) * 0.3
        mouthRef.current.scale.set(mouthScale, 1, 1)
      }
    } else {
      // 静止时轻微点头
      if (headRef.current) {
        headRef.current.rotation.x = Math.sin(time * 0.5) * 0.02
      }
    }

    // 眨眼动画
    const blinkTime = Math.floor(time * 2) % 5
    if (blinkTime === 0 && leftEyeRef.current && rightEyeRef.current) {
      const blinkScale = Math.max(0.1, Math.abs(Math.sin(time * 20)))
      leftEyeRef.current.scale.y = blinkScale
      rightEyeRef.current.scale.y = blinkScale
    } else if (leftEyeRef.current && rightEyeRef.current) {
      leftEyeRef.current.scale.y = 1
      rightEyeRef.current.scale.y = 1
    }
  })

  // 根据情绪调整面部特征
  const mouthCurve = useMemo(() => {
    switch (emotion) {
      case 'happy':
        return new THREE.Shape()
          .moveTo(-0.1, 0)
          .quadraticCurveTo(0, -0.05, 0.1, 0)
      case 'thinking':
        return new THREE.Shape()
          .moveTo(-0.08, 0.02)
          .lineTo(0.08, -0.02)
      default:
        return new THREE.Shape()
          .moveTo(-0.08, 0)
          .lineTo(0.08, 0)
    }
  }, [emotion])

  return (
    <group ref={groupRef}>
      {/* 头部 */}
      <mesh ref={headRef} position={[0, 1.6, 0]}>
        <sphereGeometry args={[0.35, 32, 32]} />
        <meshStandardMaterial color={color} />

        {/* 左眼 */}
        <mesh ref={leftEyeRef} position={[-0.12, 0.1, 0.3]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>

        {/* 右眼 */}
        <mesh ref={rightEyeRef} position={[0.12, 0.1, 0.3]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>

        {/* 嘴巴 */}
        <mesh ref={mouthRef} position={[0, -0.1, 0.32]}>
          <extrudeGeometry
            args={[
              mouthCurve,
              { depth: 0.02, bevelEnabled: false }
            ]}
          />
          <meshStandardMaterial color="#ff6b9d" />
        </mesh>
      </mesh>

      {/* 颈部 */}
      <mesh position={[0, 1.25, 0]}>
        <cylinderGeometry args={[0.12, 0.15, 0.2, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* 身体 */}
      <mesh position={[0, 0.7, 0]}>
        <capsuleGeometry args={[0.35, 0.8, 16, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* 左臂 */}
      <group position={[-0.45, 1.0, 0]}>
        {/* 上臂 */}
        <mesh position={[0, -0.25, 0]} rotation={[0, 0, Math.PI / 8]}>
          <capsuleGeometry args={[0.08, 0.4, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* 下臂 */}
        <mesh position={[-0.08, -0.6, 0]} rotation={[0, 0, Math.PI / 12]}>
          <capsuleGeometry args={[0.07, 0.35, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* 手 */}
        <mesh position={[-0.1, -0.85, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>

      {/* 右臂 */}
      <group position={[0.45, 1.0, 0]}>
        <mesh position={[0, -0.25, 0]} rotation={[0, 0, -Math.PI / 8]}>
          <capsuleGeometry args={[0.08, 0.4, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        <mesh position={[0.08, -0.6, 0]} rotation={[0, 0, -Math.PI / 12]}>
          <capsuleGeometry args={[0.07, 0.35, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        <mesh position={[0.1, -0.85, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>

      {/* 左腿 */}
      <group position={[-0.15, 0.2, 0]}>
        {/* 大腿 */}
        <mesh position={[0, -0.25, 0]}>
          <capsuleGeometry args={[0.12, 0.45, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* 小腿 */}
        <mesh position={[0, -0.65, 0]}>
          <capsuleGeometry args={[0.1, 0.4, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* 脚 */}
        <mesh position={[0, -0.95, 0.08]}>
          <boxGeometry args={[0.12, 0.08, 0.25]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>

      {/* 右腿 */}
      <group position={[0.15, 0.2, 0]}>
        <mesh position={[0, -0.25, 0]}>
          <capsuleGeometry args={[0.12, 0.45, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        <mesh position={[0, -0.65, 0]}>
          <capsuleGeometry args={[0.1, 0.4, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        <mesh position={[0, -0.95, 0.08]}>
          <boxGeometry args={[0.12, 0.08, 0.25]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>
    </group>
  )
}
