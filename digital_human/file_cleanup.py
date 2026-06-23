"""
文件清理服务 — 定时清理过期的音频和视频文件
"""
import os
import time
import asyncio
from pathlib import Path
from typing import List

# 音频和视频目录
AUDIO_DIR = Path(__file__).parent / "audio"
VIDEO_DIR = Path(__file__).parent / "videos"

# 文件最大保留时间（秒）
MAX_AGE_SECONDS = 3600  # 1小时

# 最大目录大小（字节），超过时按 LRU 删除
MAX_DIR_SIZE_MB = 500

# 清理间隔（秒）
CLEANUP_INTERVAL = 600  # 10分钟


def _get_file_age(filepath: Path) -> float:
    """获取文件年龄（秒）"""
    return time.time() - filepath.stat().st_mtime


def _cleanup_dir(dir_path: Path, max_age: float = MAX_AGE_SECONDS) -> int:
    """
    清理目录中的过期文件

    Returns:
        清理的文件数量
    """
    if not dir_path.exists():
        return 0

    deleted = 0
    files = []

    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        if f.name.startswith("."):
            continue

        # 按年龄清理
        if _get_file_age(f) > max_age:
            try:
                f.unlink()
                deleted += 1
            except Exception:
                pass
        else:
            files.append(f)

    # 按目录大小清理（LRU）
    total_size = sum(f.stat().st_size for f in files)
    max_size_bytes = MAX_DIR_SIZE_MB * 1024 * 1024

    if total_size > max_size_bytes:
        # 按修改时间排序，最旧的先删
        files.sort(key=lambda f: f.stat().st_mtime)
        for f in files:
            if total_size <= max_size_bytes:
                break
            try:
                size = f.stat().st_size
                f.unlink()
                total_size -= size
                deleted += 1
            except Exception:
                pass

    return deleted


async def cleanup_old_files():
    """清理过期的音频和视频文件"""
    audio_deleted = _cleanup_dir(AUDIO_DIR)
    video_deleted = _cleanup_dir(VIDEO_DIR)
    if audio_deleted or video_deleted:
        print(f"[清理] 删除 {audio_deleted} 个音频文件, {video_deleted} 个视频文件")


async def start_cleanup_task():
    """启动后台清理任务"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        try:
            await cleanup_old_files()
        except Exception as e:
            print(f"[清理] 失败: {e}")


def start_cleanup_background():
    """在后台启动清理任务（非阻塞）"""
    asyncio.create_task(start_cleanup_task())