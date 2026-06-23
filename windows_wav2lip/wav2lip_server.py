"""
Wav2Lip 远程推理服务 — 运行在 Windows + RTX 3050 上
接收图片 + 音频 → 返回口型同步视频

启动方式: python wav2lip_server.py --port 8001
"""
import os
import sys
import uuid
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from contextlib import asynccontextmanager

import numpy as np
import cv2
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 配置
# ============================================================
# Wav2Lip 仓库路径（安装脚本会自动 clone）
WAV2LIP_DIR = Path(__file__).parent / "Wav2Lip"
MODEL_PATH = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 推理参数
IMG_SIZE = 96         # Wav2Lip 人脸裁剪尺寸
FPS = 25              # 输出视频帧率
PAD_TOP = 0
PAD_BOTTOM = 10       # 下巴区域
PAD_LEFT = 0
PAD_RIGHT = 0

# ============================================================
# 工具函数
# ============================================================

def check_environment():
    """检查运行环境"""
    errors = []
    
    # 检查 CUDA
    try:
        import torch
        if not torch.cuda.is_available():
            errors.append("CUDA 不可用，请检查 NVIDIA 驱动和 CUDA 安装")
        else:
            print(f"[OK] CUDA: {torch.cuda.get_device_name(0)}")
    except ImportError:
        errors.append("PyTorch 未安装")
    
    # 检查 Wav2Lip
    if not WAV2LIP_DIR.exists():
        errors.append(f"Wav2Lip 目录不存在: {WAV2LIP_DIR}")
    
    # 检查模型
    if not MODEL_PATH.exists():
        errors.append(f"Wav2Lip 模型未下载: {MODEL_PATH}")
    
    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("[OK] ffmpeg 可用")
    except:
        errors.append("ffmpeg 未安装或不在 PATH 中")
    
    if errors:
        print("\n[ERROR] 环境检查失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    
    print("[OK] 环境检查通过\n")


def image_to_video(image_path: Path, audio_duration: float, output_path: Path) -> Path:
    """将单张图片转换为与音频等长的静音视频"""
    total_frames = int(audio_duration * FPS) + 5  # 多留 5 帧
    
    img = cv2.imread(str(image_path))
    if img is None:
        raise RuntimeError(f"无法读取图片: {image_path}")
    
    h, w = img.shape[:2]
    
    temp_video = TEMP_DIR / f"{uuid.uuid4().hex}.mp4"
    
    # 用 ffmpeg 从图片生成视频
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-c:v", "libx264",
        "-t", str(audio_duration + 0.5),
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 图片转视频失败: {result.stderr}")
    
    return output_path


def run_wav2lip(face_video: Path, audio_path: Path, output_path: Path):
    """调用 Wav2Lip 推理"""
    # 将 Wav2Lip 目录加入 sys.path
    sys.path.insert(0, str(WAV2LIP_DIR))
    
    import torch
    from models import Wav2Lip
    import audio as wav2lip_audio
    
    device = "cuda"
    
    print(f"[Wav2Lip] 加载模型 {MODEL_PATH}...")
    model = Wav2Lip()
    
    if torch.cuda.is_available():
        checkpoint = torch.load(MODEL_PATH)
    else:
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    
    s = checkpoint["state_dict"]
    new_s = {}
    for k, v in s.items():
        new_s[k.replace("module.", "")] = v
    model.load_state_dict(new_s)
    model = model.to(device)
    model.eval()
    
    print(f"[Wav2Lip] 读取音频: {audio_path}")
    mel = wav2lip_audio.melspectrogram(str(audio_path))
    mel_chunks = []
    mel_idx_multiplier = 80.0 / FPS
    mel_step_size = 16
    
    i = 0
    while True:
        start_idx = int(i * mel_idx_multiplier)
        if start_idx + mel_step_size > len(mel[0]):
            mel_chunks.append(mel[:, len(mel[0]) - mel_step_size:])
            break
        mel_chunks.append(mel[:, start_idx:start_idx + mel_step_size])
        i += 1
    
    print(f"[Wav2Lip] 读取视频: {face_video}")
    video_stream = cv2.VideoCapture(str(face_video))
    full_frames = []
    
    while True:
        ret, frame = video_stream.read()
        if not ret:
            break
        full_frames.append(frame)
    video_stream.release()
    
    print(f"[Wav2Lip] 检测人脸...")
    import face_detection
    detector = face_detection.FaceAlignment(
        face_detection.LandmarksType.TWO_D,
        flip_input=False,
        device=device
    )
    
    batch_size = 128
    gen = datagen(full_frames, mel_chunks, detector, device, batch_size)
    
    print(f"[Wav2Lip] 开始推理（{len(full_frames)} 帧）...")
    start_time = time.time()
    
    out = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (full_frames[0].shape[1], full_frames[0].shape[0])
    )
    
    frame_count = 0
    for i, (img_batch, mel_batch, frames, coords) in enumerate(gen):
        img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2))).to(device)
        mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2))).to(device)
        
        with torch.no_grad():
            pred = model(mel_batch, img_batch)
        
        pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.0
        
        for p, f, c in zip(pred, frames, coords):
            y1, y2, x1, x2 = c
            p_resized = cv2.resize(p.astype(np.uint8), (x2 - x1, y2 - y1))
            f[y1:y2, x1:x2] = p_resized
            out.write(f)
            frame_count += 1
    
    out.release()
    elapsed = time.time() - start_time
    print(f"[Wav2Lip] 推理完成: {frame_count} 帧, 耗时 {elapsed:.1f}s ({frame_count/elapsed:.1f} fps)")


def datagen(frames, mels, detector, device, batch_size):
    """Wav2Lip 数据生成器"""
    img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
    
    face_det_results = []
    
    # 检测所有帧的人脸
    for frame in frames:
        results = detector.get_detections_for_batch(np.expand_dims(frame, 0))
        face_det_results.append(results)
    
    for i, (frame, results) in enumerate(zip(frames, face_det_results)):
        if results is None or len(results) == 0:
            continue
        
        idx = 0 if i == 0 else min(i % len(mels), len(mels) - 1)
        
        for rect in results:
            x1 = max(0, int(rect[0]))
            y1 = max(0, int(rect[1]))
            x2 = min(frame.shape[1], int(rect[2]))
            y2 = min(frame.shape[0], int(rect[3]))
            
            face = frame[y1:y2, x1:x2]
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            
            img_batch.append(face_resized)
            mel_batch.append(mels[idx])
            frame_batch.append(frame.copy())
            coords_batch.append((y1, y2, x1, x2))
            
            if len(img_batch) >= batch_size:
                img_batch_array = np.asarray(img_batch)
                mel_batch_array = np.asarray(mel_batch)
                yield img_batch_array, mel_batch_array, frame_batch, coords_batch
                img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
    
    if len(img_batch) > 0:
        img_batch_array = np.asarray(img_batch)
        mel_batch_array = np.asarray(mel_batch)
        yield img_batch_array, mel_batch_array, frame_batch, coords_batch


# ============================================================
# FastAPI 服务
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("  Wav2Lip 远程推理服务 v1.0")
    print("  运行在: Windows + RTX 3050 (CUDA)")
    print("=" * 50)
    check_environment()
    yield
    print("服务已关闭")


app = FastAPI(
    title="Wav2Lip Remote Inference",
    description="接收图片+音频，返回口型同步视频",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """健康检查"""
    import torch
    return {
        "service": "Wav2Lip Remote Inference",
        "status": "running",
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        "model_loaded": MODEL_PATH.exists(),
    }


@app.post("/generate")
async def generate_video(
    image: UploadFile = File(..., description="教师照片 (JPG/PNG)"),
    audio: UploadFile = File(..., description="TTS 音频 (MP3/WAV)"),
):
    """
    生成口型同步视频

    请求: multipart/form-data
      - image: 教师照片
      - audio: TTS 生成的音频

    返回: MP4 视频文件
    """
    job_id = uuid.uuid4().hex
    
    # 保存上传文件
    img_ext = image.filename.rsplit(".", 1)[-1] if "." in (image.filename or "") else "jpg"
    aud_ext = audio.filename.rsplit(".", 1)[-1] if "." in (audio.filename or "") else "mp3"
    
    img_path = TEMP_DIR / f"{job_id}_input.{img_ext}"
    aud_path = TEMP_DIR / f"{job_id}_input.{aud_ext}"
    
    img_data = await image.read()
    aud_data = await audio.read()
    
    with open(img_path, "wb") as f:
        f.write(img_data)
    with open(aud_path, "wb") as f:
        f.write(aud_data)
    
    try:
        # 获取音频时长
        import soundfile as sf
        audio_info = sf.info(str(aud_path))
        duration = audio_info.duration
        print(f"[Job {job_id}] 音频时长: {duration:.1f}s")
        
        # 图片 → 视频
        face_video = TEMP_DIR / f"{job_id}_face.mp4"
        print(f"[Job {job_id}] 图片转视频...")
        image_to_video(img_path, duration, face_video)
        
        # Wav2Lip 推理
        output_video = OUTPUT_DIR / f"{job_id}.mp4"
        print(f"[Job {job_id}] Wav2Lip 推理中...")
        run_wav2lip(face_video, aud_path, output_video)
        
        # 清理临时文件
        img_path.unlink(missing_ok=True)
        aud_path.unlink(missing_ok=True)
        face_video.unlink(missing_ok=True)
        
        print(f"[Job {job_id}] 完成! 输出: {output_video}")
        
        return FileResponse(
            path=str(output_video),
            media_type="video/mp4",
            filename=f"talking_{job_id[:8]}.mp4",
            headers={"X-Job-ID": job_id},
        )
        
    except Exception as e:
        # 清理
        for p in [img_path, aud_path]:
            p.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Wav2Lip 推理失败: {str(e)}")


@app.get("/jobs")
async def list_jobs():
    """列出已生成的视频"""
    jobs = []
    for f in sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
        jobs.append({
            "id": f.stem,
            "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
            "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f.stat().st_mtime)),
        })
    return {"count": len(jobs), "jobs": jobs[:20]}


@app.get("/video/{job_id}")
async def get_video(job_id: str):
    """获取已生成的视频文件"""
    video_path = OUTPUT_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频不存在")
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001, help="服务端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址")
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)