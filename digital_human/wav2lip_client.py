"""
Wav2Lip 远程调用客户端 — 在 Mac 端调用 Windows 服务器
"""
import os
import httpx
from pathlib import Path
from typing import Optional

# Wav2Lip Windows 服务器地址
# 本地开发时设为 None（跳过调用），Windows 部署后改为实际地址
# Tailscale 示例: "http://100.64.x.x:8001"
# 局域网示例: "http://192.168.1.x:8001"
WAV2LIP_SERVER_URL = os.environ.get("WAV2LIP_SERVER_URL", None)

# 视频输出目录
OUTPUT_DIR = Path(__file__).parent / "videos"
OUTPUT_DIR.mkdir(exist_ok=True)


async def health_check() -> dict:
    """检查 Windows 服务是否在线"""
    if not WAV2LIP_SERVER_URL:
        return {"available": False, "reason": "未配置 WAV2LIP_SERVER_URL"}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{WAV2LIP_SERVER_URL}/")
            data = resp.json()
            return {
                "available": True,
                "gpu": data.get("gpu_name", "Unknown"),
                "cuda": data.get("cuda_available", False),
            }
    except Exception as e:
        return {"available": False, "reason": str(e)}


async def generate_video(
    image_path: Path,
    audio_path: Path,
    timeout: float = 120.0,
) -> Optional[Path]:
    """
    调用 Windows Wav2Lip 服务生成口型同步视频
    
    Args:
        image_path: 教师照片路径
        audio_path: TTS 音频路径
        timeout: 超时时间（秒），推理可能需要 30-120 秒
    
    Returns:
        生成的视频路径，失败返回 None
    """
    if not WAV2LIP_SERVER_URL:
        print("[Wav2Lip Client] 未配置服务器地址，跳过")
        return None
    
    print(f"[Wav2Lip Client] 发送请求到 {WAV2LIP_SERVER_URL}")
    print(f"  图片: {image_path} ({image_path.stat().st_size / 1024:.0f}KB)")
    print(f"  音频: {audio_path} ({audio_path.stat().st_size / 1024:.0f}KB)")
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            with open(image_path, "rb") as img_f, open(audio_path, "rb") as aud_f:
                files = {
                    "image": (image_path.name, img_f, "image/jpeg"),
                    "audio": (audio_path.name, aud_f, "audio/mpeg"),
                }
                resp = await client.post(
                    f"{WAV2LIP_SERVER_URL}/generate",
                    files=files,
                )
            
            if resp.status_code == 200:
                # 保存视频
                video_name = f"{Path(audio_path).stem}.mp4"
                video_path = OUTPUT_DIR / video_name
                with open(video_path, "wb") as f:
                    f.write(resp.content)
                print(f"[Wav2Lip Client] 视频已保存: {video_path}")
                return video_path
            else:
                print(f"[Wav2Lip Client] 服务器返回错误: {resp.status_code}")
                print(f"  {resp.text[:500]}")
                return None
                
    except httpx.TimeoutException:
        print(f"[Wav2Lip Client] 请求超时 ({timeout}s)")
        return None
    except Exception as e:
        print(f"[Wav2Lip Client] 调用失败: {e}")
        return None


def get_video_url(video_path: Optional[Path]) -> Optional[str]:
    """本地视频路径 → HTTP URL"""
    if video_path is None:
        return None
    # 返回相对于 digital_human/videos/ 的 URL
    return f"/digital_human/videos/{video_path.name}"