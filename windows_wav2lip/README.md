# Wav2Lip Windows 部署指南

## 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 |
| GPU | NVIDIA RTX 3050 Laptop (4GB VRAM) |
| 驱动 | NVIDIA 驱动 526.00+ |
| CUDA | 11.8 |
| Python | 3.9 |
| 磁盘 | 至少 5GB 空闲空间 |
| 网络 | 能访问 GitHub、PyPI |

## 快速开始

### 1. 安装 CUDA 11.8

下载并安装: https://developer.nvidia.com/cuda-11-8-0-download-archive

选择: Windows → x86_64 → 10 → exe(local)

### 2. 运行一键安装脚本

```bat
双击 setup.bat
```

脚本会自动:
- 检查 Python 和 CUDA 环境
- 安装 PyTorch (CUDA 11.8) 和所有依赖
- 克隆 Wav2Lip 仓库

### 3. 手动下载模型文件

脚本会提示下载两个模型文件:

**Wav2Lip 模型** (约 380MB):
- 下载: https://drive.google.com/drive/folders/1tBkqi4yuFgsmduxq3qNnN0itaqoJ_Bb0
- 放置: `Wav2Lip/checkpoints/wav2lip_gan.pth`

**人脸检测模型** (约 10MB):
- 下载: https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth
- 重命名为: `s3fd.pth`
- 放置: `Wav2Lip/face_detection/detection/sfd/s3fd.pth`

### 4. 启动服务

```bat
双击 start_server.bat
```

或命令行:
```bat
python wav2lip_server.py --port 8001
```

### 5. 测试

```bash
# 健康检查
curl http://localhost:8001/

# 生成视频
curl -X POST http://localhost:8001/generate \
  -F "image=@teacher.jpg" \
  -F "audio=@speech.mp3" \
  -o output.mp4
```

## 远程访问（Tailscale）

### 安装 Tailscale

1. 两台电脑都安装 Tailscale: https://tailscale.com/download
2. 登录同一个账号
3. Windows 会自动分配一个虚拟 IP（如 `100.64.x.x`）

### Mac 端配置

获取 Windows 的 Tailscale IP:
```bash
# Windows 命令行
tailscale ip -4
```

然后在 Mac 上测试:
```bash
curl http://100.64.x.x:8001/
```

## 目录结构

```
windows_wav2lip/
├── setup.bat              # 一键安装脚本
├── start_server.bat       # 启动脚本
├── wav2lip_server.py      # API 服务
├── requirements.txt       # 依赖列表
├── Wav2Lip/               # Wav2Lip 仓库
│   ├── checkpoints/
│   │   └── wav2lip_gan.pth
│   └── face_detection/
│       └── detection/sfd/
│           └── s3fd.pth
├── outputs/               # 生成的视频
└── temp/                  # 临时文件
```

## 推理性能

RTX 3050 Laptop (4GB) 实测:
- 10 秒音频 → 约 30-60 秒推理
- 25 秒音频 → 约 1-2 分钟推理
- 显存占用: 约 2.5GB

## 常见问题

**Q: 报错 "CUDA not available"**
A: 检查 NVIDIA 驱动是否安装，运行 `nvidia-smi` 确认

**Q: 人脸检测失败**
A: 确保照片是正面、清晰的人脸，光照充足

**Q: 显存不足**
A: 减小 batch_size（修改 `wav2lip_server.py` 中的 `batch_size` 变量为 64 或 32）