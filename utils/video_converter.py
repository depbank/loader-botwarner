"""
Конвертер видео в кружочек (Video → Round)
"""
import os
import asyncio
import subprocess
import logging
import config

logger = logging.getLogger(__name__)

# Semaphore для ограничения одновременных конверсий
video_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_VIDEO_CONVERSIONS)


async def get_video_duration(file_path: str) -> float:
    """Получить длительность видео в секундах"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_duration_sync, file_path)


def _get_duration_sync(file_path: str) -> float:
    """Синхронное получение длительности"""
    try:
        result = subprocess.run(
            [config.FFPROBE_PATH, '-v', 'error', '-show_entries',
             'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Duration error: {e}")
        return 0


async def convert_to_round_video(input_path: str, output_path: str):
    """Конвертировать видео в круглый формат (кружочек)"""
    async with video_semaphore:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _convert_sync, input_path, output_path)


def _convert_sync(input_path: str, output_path: str):
    """Синхронная конвертация через FFmpeg"""
    size = config.ROUND_VIDEO_SIZE

    cmd = [
        config.FFMPEG_PATH, '-y',
        '-i', input_path,
        '-vf', f'crop={size}:{size}:((iw-{size})/2):((ih-{size})/2),format=yuv420p',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-b:v', '1M',
        '-maxrate', '1.5M',
        '-bufsize', '2M',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-t', '15',
        '-shortest',
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr[:200]}")
            raise Exception(f"FFmpeg error: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        raise Exception("Конвертация превысила лимит времени (120с)")
    except Exception as e:
        raise Exception(f"Ошибка конвертации: {e}")
