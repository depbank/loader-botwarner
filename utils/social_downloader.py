"""
Социальный загрузчик — TikTok, Instagram, YouTube
"""
import os
import asyncio
import logging
import re
from yt_dlp import YoutubeDL
import config

logger = logging.getLogger(__name__)


class SocialDownloader:
    """Загрузчик видео из соцсетей через yt-dlp"""

    SUPPORTED_DOMAINS = [
        'tiktok.com', 'vm.tiktok.com',
        'instagram.com', 'www.instagram.com',
        'youtube.com', 'm.youtube.com', 'www.youtube.com',
        'youtu.be',
        'facebook.com', 'www.facebook.com',
        'twitter.com', 'x.com',
        'reddit.com', 'www.reddit.com',
        'vimeo.com',
    ]

    def is_supported_url(self, url: str) -> bool:
        """Проверяет, поддерживается ли ссылка"""
        return any(domain in url.lower() for domain in self.SUPPORTED_DOMAINS)

    async def get_video_info(self, url: str) -> dict:
        """Получить информацию о видео"""
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._get_info_sync, url)
        return info

    def _get_info_sync(self, url: str) -> dict:
        """Синхронное получение информации"""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Video'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                }
        except Exception as e:
            logger.error(f"Info error: {e}")
            return {'title': 'Video', 'duration': 0, 'view_count': 0}

    async def download(self, url: str, output_template: str) -> dict:
        """Скачать видео"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._download_sync, url, output_template)
        return result

    def _download_sync(self, url: str, output_template: str) -> dict:
        """Синхронная загрузка"""
        ydl_opts = {
            'format': config.YTDLP_FORMAT,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'restrictfilenames': True,
            'max_filesize': 50 * 1024 * 1024,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # Ищем фактический файл
                base = os.path.splitext(filename)[0]
                for ext in ['.mp4', '.mkv', '.webm', '.mov']:
                    test_path = base + ext
                    if os.path.exists(test_path):
                        return {
                            'filepath': test_path,
                            'title': info.get('title', 'Video')[:50],
                        }

                # Если файл не найден, ищем любой mp4
                for f in os.listdir(config.DOWNLOADS_DIR):
                    if f.startswith(os.path.basename(base)) and f.endswith('.mp4'):
                        return {
                            'filepath': os.path.join(config.DOWNLOADS_DIR, f),
                            'title': info.get('title', 'Video')[:50],
                        }

                return {'filepath': '', 'title': 'Video'}

        except Exception as e:
            logger.error(f"Download error: {e}")
            raise


downloader = SocialDownloader()
