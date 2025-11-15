import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface ImprovedCharacterProps {
  color: string
  isSpeaking?: boolean
  emotion?: 'happy' | 'neutral' | 'thinking'
}

/**
 * Improved 3D humanoid character component
 * Features:
 * - More humanoid proportions
 * - Facial expressions (eyes, mouth)
 * - Animations when speaking
 * - Breathing effects
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

  // Animation logic
  useFrame((state) => {
    if (!groupRef.current) return

    const time = state.clock.getElapsedTime()

    // Gentle swaying (breathing effect)
    groupRef.current.position.y = Math.sin(time * 1.5) * 0.05

    // Head animation when speaking
    if (isSpeaking && headRef.current) {
      headRef.current.rotation.x = Math.sin(time * 10) * 0.05

      // Mouth opening and closing
      if (mouthRef.current) {
        const mouthScale = 1 + Math.abs(Math.sin(time * 12)) * 0.3
        mouthRef.current.scale.set(mouthScale, 1, 1)
      }
    } else {
      // Gentle nodding when idle
      if (headRef.current) {
        headRef.current.rotation.x = Math.sin(time * 0.5) * 0.02
      }
    }

    // Blinking animation
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

  // Adjust facial features based on emotion
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
      {/* Head */}
      <mesh ref={headRef} position={[0, 1.6, 0]}>
        <sphereGeometry args={[0.35, 32, 32]} />
        <meshStandardMaterial color={color} />

        {/* Left eye */}
        <mesh ref={leftEyeRef} position={[-0.12, 0.1, 0.3]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>

        {/* Right eye */}
        <mesh ref={rightEyeRef} position={[0.12, 0.1, 0.3]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>

        {/* Mouth */}
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

      {/* Neck */}
      <mesh position={[0, 1.25, 0]}>
        <cylinderGeometry args={[0.12, 0.15, 0.2, 16]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Body */}
      <mesh position={[0, 0.7, 0]}>
        <capsuleGeometry args={[0.35, 0.8, 16, 32]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* Left arm */}
      <group position={[-0.45, 1.0, 0]}>
        {/* Upper arm */}
        <mesh position={[0, -0.25, 0]} rotation={[0, 0, Math.PI / 8]}>
          <capsuleGeometry args={[0.08, 0.4, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* Lower arm */}
        <mesh position={[-0.08, -0.6, 0]} rotation={[0, 0, Math.PI / 12]}>
          <capsuleGeometry args={[0.07, 0.35, 8, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* Hand */}
        <mesh position={[-0.1, -0.85, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>

      {/* Right arm */}
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

      {/* Left leg */}
      <group position={[-0.15, 0.2, 0]}>
        {/* Thigh */}
        <mesh position={[0, -0.25, 0]}>
          <capsuleGeometry args={[0.12, 0.45, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* Calf */}
        <mesh position={[0, -0.65, 0]}>
          <capsuleGeometry args={[0.1, 0.4, 12, 16]} />
          <meshStandardMaterial color={color} />
        </mesh>
        {/* Foot */}
        <mesh position={[0, -0.95, 0.08]}>
          <boxGeometry args={[0.12, 0.08, 0.25]} />
          <meshStandardMaterial color={color} />
        </mesh>
      </group>

      {/* Right leg */}
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
