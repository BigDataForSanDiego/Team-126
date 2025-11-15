import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface GLBCharacterProps {
  modelPath: string
  isSpeaking?: boolean
  animationName?: string
}

/**
 * 通用的GLB/GLTF模型加载组件
 *
 * 使用方法：
 * 1. 从以下网站下载免费3D模型：
 *    - Mixamo (https://www.mixamo.com/) - 带动画的人物模型
 *    - Sketchfab (https://sketchfab.com/) - 免费3D模型库
 *    - Ready Player Me (https://readyplayer.me/) - 自定义头像
 *
 * 2. 将.glb文件放在 /public/models/ 目录下
 *
 * 3. 使用：
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
    // 播放指定动画
    if (isSpeaking && actions['talking']) {
      actions['talking']?.play()
    } else if (actions[animationName]) {
      actions[animationName]?.play()
    } else if (names.length > 0) {
      // 如果没有找到指定动画，播放第一个动画
      actions[names[0]]?.play()
    }

    return () => {
      // 清理动画
      Object.values(actions).forEach(action => action?.stop())
    }
  }, [actions, animationName, isSpeaking, names])

  return (
    <group ref={group}>
      <primitive object={scene} />
    </group>
  )
}

// 预加载模型以提升性能
export function preloadModel(modelPath: string) {
  useGLTF.preload(modelPath)
}
