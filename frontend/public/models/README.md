# 3D Models Directory

## 📁 如何使用

将你的 `.glb` 或 `.gltf` 3D模型文件放在这个目录下。

## 🚀 快速测试

### 使用 Ready Player Me（推荐 - 无需下载文件）

1. 访问：https://readyplayer.me/
2. 创建头像
3. 复制URL
4. 修改 `src/pages/Chat.tsx`:

```typescript
const CHARACTER_CONFIG = {
  type: 'readyplayerme',
  readyPlayerMeUrl: '你的URL',
}
```

### 使用本地GLB文件

1. 下载 `.glb` 文件
2. 复制到这个目录：
   ```bash
   cp ~/Downloads/my-character.glb /Users/jason/Documents/Area/GitHub/Team-126/frontend/public/models/
   ```
3. 修改配置：
   ```typescript
   const CHARACTER_CONFIG = {
     type: 'glb',
     glbModelPath: '/models/my-character.glb',
   }
   ```

## 🎨 免费模型资源

### Ready Player Me（最简单）
- 网址：https://readyplayer.me/
- 特点：在线创建，无需下载
- 质量：⭐⭐⭐⭐⭐

### Mixamo（专业动画）
- 网址：https://www.mixamo.com/
- 特点：Adobe官方，带动画
- 质量：⭐⭐⭐⭐⭐
- 需要：Adobe账号（免费）

### Sketchfab（多样选择）
- 网址：https://sketchfab.com/
- 搜索：low poly character + downloadable + free
- 质量：⭐⭐⭐⭐
- 筛选：选择 CC 许可证

### Poly Pizza（低多边形）
- 网址：https://poly.pizza/
- 特点：100%免费，低多边形
- 质量：⭐⭐⭐
- 优点：加载超快

## 📝 文件命名建议

```
models/
  ├── assistant-male.glb      # 男性助手
  ├── assistant-female.glb    # 女性助手
  ├── character-1.glb         # 角色1
  ├── character-2.glb         # 角色2
  └── README.md               # 本文件
```

## ⚠️ 注意事项

- 推荐使用 `.glb` 格式（单文件）
- 模型文件建议 < 5MB
- 多边形数建议 < 10k triangles
- 贴图分辨率建议 512x512 或 1024x1024

## 🛠️ 文件格式转换

如果你有 `.fbx` 或其他格式：

### 在线转换
访问：https://products.aspose.app/3d/conversion/fbx-to-glb

### 使用 Blender
1. 安装 Blender（免费）：https://www.blender.org/
2. 导入你的模型：File → Import
3. 导出为GLB：File → Export → glTF 2.0 (.glb)

## 📚 更多信息

查看项目根目录的 `BEAUTIFUL_CHARACTERS_GUIDE.md` 获取详细指南。
