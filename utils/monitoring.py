"""
Мониторинг системы — CPU, RAM, диск
"""
import psutil
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Мониторинг системных ресурсов"""

    async def get_stats(self) -> dict:
        """Получить статистику системы"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_stats_sync)

    def _get_stats_sync(self) -> dict:
        """Синхронный сбор статистики"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.5),
            'cpu_count': psutil.cpu_count(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent,
            },
            'uptime': datetime.now().timestamp() - psutil.boot_time(),
            'timestamp': datetime.now().isoformat(),
        }

    async def get_formatted_stats(self) -> str:
        """Получить отформатированную статистику"""
        stats = await self.get_stats()
        cpu_bar = self._progress_bar(stats['cpu_percent'])
        mem_bar = self._progress_bar(stats['memory']['percent'])
        disk_bar = self._progress_bar(stats['disk']['percent'])

        uptime_seconds = stats['uptime']
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)

        return (
            f"📊 <b>Мониторинг системы</b>\n\n"
            f"🖥 <b>CPU:</b> {stats['cpu_percent']}%\n{cpu_bar}\n"
            f"💾 <b>RAM:</b> {stats['memory']['percent']}%\n{mem_bar}\n"
            f"💿 <b>Диск:</b> {stats['disk']['percent']}%\n{disk_bar}\n\n"
            f"⏱ Uptime: {int(days)}д {int(hours)}ч {int(minutes)}м\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def _progress_bar(self, percent: float, width: int = 15) -> str:
        filled = int(percent / 100 * width)
        bar = "▓" * filled + "░" * (width - filled)
        return f"<code>[{bar}]</code>"


monitor = SystemMonitor()
