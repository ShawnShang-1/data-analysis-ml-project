"""
数字人语音合成服务 — edge-tts 集成
"""
import asyncio
import os
import uuid
import edge_tts
from pathlib import Path

# 音频输出目录
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 中文语音选项
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 温柔女声（推荐）
    "yunxi": "zh-CN-YunxiNeural",            # 活泼男声
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 年轻女声（推荐）
    "yunyang": "zh-CN-YunyangNeural",        # 新闻男声
    "henan": "zh-CN-henan-YundengNeural",    # 河南方言
}

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


async def synthesize_speech(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+10%",
    output_dir: str = None,
) -> dict:
    """
    使用 edge-tts 将文本转为语音

    Args:
        text: 要合成的文本
        voice: 语音角色，默认 zh-CN-XiaoxiaoNeural
        rate: 语速调节，如 "+10%" 加速 10%，"-10%" 减速 10%
        output_dir: 输出目录，默认为 audio/

    Returns:
        {
            "audio_path": str,      # 音频文件路径
            "audio_url": str,       # 音频访问 URL（相对路径）
            "duration": float,      # 音频时长（秒）
            "text": str,            # 原始文本
            "voice": str,           # 使用的语音
        }
    """
    if not text or not text.strip():
        raise ValueError("文本不能为空")

    dir_path = Path(output_dir) if output_dir else AUDIO_DIR
    dir_path.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:12]}.mp3"
    filepath = dir_path / filename

    communicate = edge_tts.Communicate(
        text=text.strip(),
        voice=voice,
        rate=rate,
        volume="+0%",
    )

    await communicate.save(str(filepath))

    # 精确计算音频时长：edge-tts 输出为 CBR 48kbps MP3
    # duration = 文件大小(字节) * 8 / 比特率
    MP3_BITRATE_BPS = 48000
    file_size = filepath.stat().st_size
    duration = file_size * 8 / MP3_BITRATE_BPS

    return {
        "audio_path": str(filepath.absolute()),
        "audio_url": f"/digital_human/audio/{filename}",
        "duration": round(duration, 2),
        "text": text.strip(),
        "voice": voice,
    }


async def get_available_voices() -> dict:
    """获取可用语音列表"""
    return VOICES


async def warmup():
    """
    预热 edge-tts — 首次调用需要下载语音字体
    建议在服务启动时调用一次
    """
    try:
        await synthesize_speech("预热", voice=DEFAULT_VOICE, output_dir=AUDIO_DIR)
        print("✅ edge-tts 预热完成")
    except Exception as e:
        print(f"⚠️ edge-tts 预热失败: {e}")