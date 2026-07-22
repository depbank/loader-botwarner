import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ==================== VALIDATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN не указан! Укажите токен в .env файле")
    print("📝 Получить токен: https://t.me/BotFather")
    sys.exit(1)

if "ВАШ" in BOT_TOKEN or "your" in BOT_TOKEN.lower():
    print("❌ BOT_TOKEN содержит placeholder! Укажите реальный токен в .env")
    sys.exit(1)

try:
    MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "0"))
except ValueError:
    print("❌ MAIN_ADMIN_ID должен быть числом!")
    sys.exit(1)

if MAIN_ADMIN_ID == 0:
    print("❌ MAIN_ADMIN_ID не указан! Укажите ваш Telegram ID в .env")
    print("📝 Получить ID: https://t.me/userinfobot")
    sys.exit(1)

# ==================== REDIS ====================
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() in ("true", "1", "yes")

# ==================== WEBHOOK ====================
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else ""
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "loader-bot-secret-2026")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
USE_WEBHOOK = bool(WEBHOOK_HOST) and os.getenv("USE_WEBHOOK", "false").lower() in ("true", "1", "yes")

# ==================== SEMAPHORE LIMITS ====================
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))
MAX_CONCURRENT_VIDEO_CONVERSIONS = int(os.getenv("MAX_CONCURRENT_VIDEO_CONVERSIONS", "2"))
MAX_CONCURRENT_BROADCASTS = int(os.getenv("MAX_CONCURRENT_BROADCASTS", "5"))

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, os.getenv("TEMP_DIR", "temp"))
DOWNLOADS_DIR = os.path.join(BASE_DIR, os.getenv("DOWNLOADS_DIR", "downloads"))
LOGS_DIR = os.path.join(BASE_DIR, os.getenv("LOGS_DIR", "logs"))
DB_PATH = os.path.join(BASE_DIR, os.getenv("DB_PATH", "database/bot.db"))

# ==================== PASSWORDS ====================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "314159")
MONITORING_PASSWORD = os.getenv("MONITORING_PASSWORD", "906301073")

# ==================== FFMPEG ====================
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")

# Локальная установка FFmpeg
_local_ffmpeg = os.path.join(BASE_DIR, "ffmpeg.exe")
_local_ffprobe = os.path.join(BASE_DIR, "ffprobe.exe")
if os.path.exists(_local_ffmpeg):
    FFMPEG_PATH = _local_ffmpeg
    FFPROBE_PATH = _local_ffprobe if os.path.exists(_local_ffprobe) else "ffprobe"

# Добавляем в PATH
_ffmpeg_dir = os.path.dirname(FFMPEG_PATH) if os.path.exists(FFMPEG_PATH) else ''
if _ffmpeg_dir and _ffmpeg_dir not in os.environ.get('PATH', ''):
    os.environ['PATH'] = _ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

# ==================== DIRECTORIES ====================
_db_dir = os.path.dirname(DB_PATH)
for directory in [TEMP_DIR, DOWNLOADS_DIR, LOGS_DIR, _db_dir]:
    if directory:
        os.makedirs(directory, exist_ok=True)

# ==================== LIMITS ====================
MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "15"))
MAX_DOWNLOAD_QUALITY = int(os.getenv("MAX_DOWNLOAD_QUALITY", "720"))

# ==================== ASCII ====================
ASCII_CHARS = "@%#*+=-:. "
ASCII_WIDTH = 100

# ==================== VIDEO ====================
ROUND_VIDEO_SIZE = 384

# ==================== DOWNLOAD ====================
YTDLP_FORMAT = f"bestvideo[height<={MAX_DOWNLOAD_QUALITY}]+bestaudio/best[height<={MAX_DOWNLOAD_QUALITY}]"
