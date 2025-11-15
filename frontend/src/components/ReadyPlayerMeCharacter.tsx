import { useGLTF } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface ReadyPlayerMeCharacterProps {
  avatarUrl: string
  isSpeaking?: boolean
  audioLevel?: number
}

/**
 * Ready Player Me 3D Avatar Component with Lip-Sync
 *
 * Usage:
 * 1. Visit https://readyplayer.me/ to create a free avatar
 * 2. Obtain the .glb file URL
 * 3. Pass it as the avatarUrl prop
 * 4. Pass audioLevel (0-1) for lip-sync animation
 */
export function ReadyPlayerMeCharacter({
  avatarUrl,
  isSpeaking = false,
  audioLevel = 0
}: ReadyPlayerMeCharacterProps) {
  const { scene } = useGLTF(avatarUrl)
  const headRef = useRef<THREE.SkinnedMesh | null>(null)

  // Find the head mesh with morph targets on mount
  useEffect(() => {
    scene.traverse((child) => {
      if (child instanceof THREE.SkinnedMesh && child.morphTargetDictionary) {
        // Look for head/face mesh (usually contains "Head" or "Wolf3D_Head" in name)
        if (child.name.toLowerCase().includes('head') ||
            child.name.toLowerCase().includes('face')) {
          headRef.current = child
          console.log('[Lip-Sync] Found head mesh:', child.name)
          console.log('[Lip-Sync] Available morph targets:', Object.keys(child.morphTargetDictionary))
        }
      }
    })
  }, [scene])

  // Animate lip-sync based on audio level
  useFrame(() => {
    if (headRef.current && headRef.current.morphTargetInfluences && isSpeaking) {
      const influences = headRef.current.morphTargetInfluences
      const dict = headRef.current.morphTargetDictionary

      // Try to find mouth open morph target (different avatars use different names)
      const mouthOpenIndex =
        dict?.['mouthOpen'] ??
        dict?.['jawOpen'] ??
        dict?.['viseme_aa'] ??
        dict?.['viseme_E'] ??
        -1

      if (mouthOpenIndex >= 0) {
        // Animate mouth based on audio level
        influences[mouthOpenIndex] = audioLevel
      }
    } else if (headRef.current && headRef.current.morphTargetInfluences && !isSpeaking) {
      // Close mouth when not speaking
      const influences = headRef.current.morphTargetInfluences
      for (let i = 0; i < influences.length; i++) {
        influences[i] = 0
      }
    }
  })

  return (
    <group scale={1.2} position={[0, -0.8, 0]}>
      <primitive object={scene} />
    </group>
  )
}
