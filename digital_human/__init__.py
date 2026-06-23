"""
数字人 API 路由 — 提供语音合成 + 视位分析 + Wav2Lip 视频生成
"""
import json
import os
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .tts_service import synthesize_speech, DEFAULT_VOICE, VOICES, AUDIO_DIR
from .viseme_analyzer import (
    generate_viseme_timeline,
    get_viseme_expression_map,
    get_expression_types,
)
from .wav2lip_client import (
    health_check,
    generate_video,
    get_video_url,
    OUTPUT_DIR as VIDEO_DIR,
    WAV2LIP_SERVER_URL,
)

router = APIRouter(prefix="/digital_human", tags=["数字人"])

ASSETS_DIR = Path(__file__).parent / "assets"


# ── 请求/响应模型 ──

class DigitalHumanRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    rate: str = "+10%"
    expression: str = "explaining"  # smiling | explaining | thinking | nodding | surprised | focusing


class DigitalHumanResponse(BaseModel):
    text: str
    audio_url: str
    audio_duration: float
    viseme_timeline: list
    expression: str
    voice: str


class TTSRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    rate: str = "+10%"


# ── API 路由 ──

@router.post("/speak", response_model=DigitalHumanResponse)
async def digital_human_speak(req: DigitalHumanRequest):
    """
    数字人说话接口 — 返回语音 + 视位时间线 + 表情

    前端调用此接口获取：
    1. 语音文件 URL（播放）
    2. 视位时间线（驱动唇形动画）
    3. 表情类型（切换面部表情）
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    try:
        # 1. 语音合成
        tts_result = await synthesize_speech(
            text=req.text.strip(),
            voice=req.voice,
            rate=req.rate,
        )

        # 2. 视位分析（CPU 密集，放到线程池避免阻塞事件循环）
        viseme_timeline = await asyncio.to_thread(
            generate_viseme_timeline,
            text=req.text.strip(),
            audio_duration=tts_result["duration"],
        )

        return DigitalHumanResponse(
            text=req.text.strip(),
            audio_url=tts_result["audio_url"],
            audio_duration=tts_result["duration"],
            viseme_timeline=viseme_timeline,
            expression=req.expression,
            voice=req.voice,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数字人合成失败: {str(e)}")


@router.post("/tts")
async def tts_only(req: TTSRequest):
    """
    纯 TTS 接口 — 仅返回语音文件
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    try:
        result = await synthesize_speech(
            text=req.text.strip(),
            voice=req.voice,
            rate=req.rate,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


def _safe_path(base_dir: Path, filename: str) -> Path:
    """安全路径校验 — 防止路径遍历攻击"""
    # 仅取文件名部分，去除任何路径分隔符
    safe_name = Path(filename).name
    if safe_name != filename or ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="非法文件名")
    filepath = (base_dir / safe_name).resolve()
    # 确保解析后的路径在目标目录内
    if not str(filepath).startswith(str(base_dir.resolve())):
        raise HTTPException(status_code=403, detail="访问被拒绝")
    return filepath


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """提供音频文件访问"""
    filepath = _safe_path(AUDIO_DIR, filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    return FileResponse(
        path=str(filepath),
        media_type="audio/mpeg",
        filename=filepath.name,
    )


@router.get("/assets/{filename}")
async def serve_asset(filename: str):
    """提供数字人资源文件（图片等）"""
    filepath = _safe_path(ASSETS_DIR, filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="资源文件不存在")
    ext = filepath.suffix.lower().lstrip(".")
    media_types = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
        "gif": "image/gif", "webp": "image/webp",
    }
    return FileResponse(
        path=str(filepath),
        media_type=media_types.get(ext, "application/octet-stream"),
    )


@router.get("/voices")
async def list_voices():
    """获取可用语音列表"""
    return {"voices": VOICES}


@router.get("/expressions")
async def list_expressions():
    """获取可用表情类型"""
    return {"expressions": get_expression_types()}


@router.get("/viseme_map")
async def viseme_map():
    """获取 viseme 到 CSS 类的映射"""
    return {"viseme_map": get_viseme_expression_map()}


@router.get("/assets_list")
async def list_assets():
    """获取可用的数字人资源文件列表"""
    if not ASSETS_DIR.exists():
        return {"assets": []}
    assets = []
    for f in ASSETS_DIR.iterdir():
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            assets.append(f.name)
    return {"assets": sorted(assets)}


# ── Wav2Lip 视频生成接口 ──

class SpeakVideoRequest(BaseModel):
    text: str
    voice: str = DEFAULT_VOICE
    rate: str = "+10%"
    expression: str = "explaining"


@router.post("/speak_video")
async def digital_human_speak_video(req: SpeakVideoRequest):
    """
    数字人说话接口（Wav2Lip 视频版）
    
    流程:
    1. Mac 本地生成 TTS 音频
    2. 发送图片+音频到 Windows Wav2Lip 服务
    3. 返回口型同步视频 URL
    
    如果 Wav2Lip 不可用，自动降级为图片切换方案
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    try:
        # 1. TTS 语音合成
        tts_result = await synthesize_speech(
            text=req.text.strip(),
            voice=req.voice,
            rate=req.rate,
        )

        # 2. 视位分析（CPU 密集，放到线程池避免阻塞事件循环）
        viseme_timeline = await asyncio.to_thread(
            generate_viseme_timeline,
            text=req.text.strip(),
            audio_duration=tts_result["duration"],
        )

        # 3. 尝试 Wav2Lip 视频生成
        video_url = None
        wav2lip_used = False

        if WAV2LIP_SERVER_URL:
            # 使用默认教师照片
            teacher_img = ASSETS_DIR / "teacher_professional.jpg"
            if not teacher_img.exists():
                # 查找任意 jpg 图片
                imgs = list(ASSETS_DIR.glob("*.jpg"))
                teacher_img = imgs[0] if imgs else None

            if teacher_img:
                audio_path = AUDIO_DIR / Path(tts_result["audio_url"]).name
                video_path = await generate_video(teacher_img, audio_path)
                if video_path:
                    video_url = get_video_url(video_path)
                    wav2lip_used = True
                    print(f"[数字人] Wav2Lip 视频已生成: {video_url}")

        return {
            "text": req.text.strip(),
            "audio_url": tts_result["audio_url"],
            "audio_duration": tts_result["duration"],
            "viseme_timeline": viseme_timeline,
            "expression": req.expression,
            "voice": req.voice,
            "video_url": video_url,
            "wav2lip_used": wav2lip_used,
            "fallback": not wav2lip_used,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数字人视频合成失败: {str(e)}")


@router.get("/videos/{filename}")
async def serve_video(filename: str):
    """提供 Wav2Lip 生成的视频文件"""
    filepath = _safe_path(VIDEO_DIR, filename)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")
    return FileResponse(
        path=str(filepath),
        media_type="video/mp4",
        filename=filepath.name,
    )


@router.get("/wav2lip_status")
async def wav2lip_status():
    """检查 Wav2Lip Windows 服务状态"""
    if not WAV2LIP_SERVER_URL:
        return {
            "configured": False,
            "message": "未配置 WAV2LIP_SERVER_URL",
            "hint": "设置环境变量或在 config.py 中配置",
        }
    
    status = await health_check()
    return {
        "configured": True,
        "server_url": WAV2LIP_SERVER_URL,
        **status,
    }