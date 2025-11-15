import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface GLBCharacterProps {
  modelPath: string
  isSpeaking?: boolean
  animationName?: string
}

/**
 * Generic GLB/GLTF model loading component
 *
 * Usage:
 * 1. Download free 3D models from the following websites:
 *    - Mixamo (https://www.mixamo.com/) - Animated character models
 *    - Sketchfab (https://sketchfab.com/) - Free 3D model library
 *    - Ready Player Me (https://readyplayer.me/) - Custom avatars
 *
 * 2. Place .glb files in the /public/models/ directory
 *
 * 3. Usage:
 *    <GLBCharacter modelPath="/models/character.glb" animationName="idle" />
 */
export function GLBCharacter({
  modelPath,
  isSpeaking = false,
  animationName = 'idle'
}: GLBCharacterProps) {
  const group = useRef<THREE.Group>(null)
  const { scene, animations } = useGLTF(modelPath)
  const { actions, names } = useAnimations(animations, group)

  useEffect(() => {
    // Play the specified animation
    if (isSpeaking && actions['talking']) {
      actions['talking']?.play()
    } else if (actions[animationName]) {
      actions[animationName]?.play()
    } else if (names.length > 0) {
      // If the specified animation is not found, play the first animation
      actions[names[0]]?.play()
    }

    return () => {
      // Clean up animations
      Object.values(actions).forEach(action => action?.stop())
    }
  }, [actions, animationName, isSpeaking, names])

  return (
    <group ref={group}>
      <primitive object={scene} />
    </group>
  )
}

// Preload models to improve performance
export function preloadModel(modelPath: string) {
  useGLTF.preload(modelPath)
}
