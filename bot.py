import asyncio
import logging
import sys
import os
from datetime import datetime

import utils.encoding_fix

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.enums import ParseMode

import config
from database import db
from keyboards import *
from utils.qr_generator import generate_qr
from utils.ascii_converter import image_to_ascii
from utils.video_converter import convert_to_round_video, get_video_duration
from utils.social_downloader import downloader
from utils.monitoring import monitor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'bot.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# ==================== FSM STATES ====================

class UserStates(StatesGroup):
    waiting_for_ascii_photo = State()
    waiting_for_ascii_video = State()
    waiting_for_round_video = State()
    waiting_for_download_url = State()
    waiting_for_qr_text = State()


class AdminStates(StatesGroup):
    waiting_for_admin_password = State()
    waiting_for_monitoring_password = State()
    waiting_for_monitoring_approval = State()

    waiting_for_broadcast_message = State()
    waiting_for_broadcast_user_id = State()

    waiting_for_ban_user_id = State()
    waiting_for_unban_user_id = State()

    waiting_for_add_admin_id = State()
    waiting_for_remove_admin_id = State()

    waiting_for_maintenance_duration = State()
    waiting_for_maintenance_reason = State()

    waiting_for_new_admin_password = State()
    waiting_for_new_monitoring_password = State()

    waiting_for_logs_user_id = State()

    # Новые состояния для админ-панели v2
    waiting_for_server_name = State()
    waiting_for_server_url = State()
    waiting_for_welcome_text = State()
    waiting_for_search_query = State()
    waiting_for_ucp_user_id = State()
    waiting_for_scheduled_text = State()
    waiting_for_scheduled_time = State()
    waiting_for_filtered_broadcast = State()


# ==================== MIDDLEWARES ====================

async def check_maintenance(handler, event, data):
    """Middleware для проверки режима техобслуживания"""
    maintenance = await db.get_setting('maintenance_mode')

    if maintenance == 'true':
        user_id = event.from_user.id if hasattr(event, 'from_user') else None

        if user_id and await db.is_admin(user_id):
            return await handler(event, data)

        if isinstance(event, Message):
            reason = await db.get_setting('maintenance_reason') or 'Плановое обслуживание'
            duration = await db.get_setting('maintenance_duration') or 'Неизвестно'

            await event.answer(
                f"🔧 <b>Бот на техническом обслуживании</b>\n\n"
                f"Причина: {reason}\n"
                f"Ориентировочное время: {duration}\n\n"
                f"Приносим извинения за неудобства!",
                reply_markup=get_contact_admin_keyboard()
            )
            return

    return await handler(event, data)


async def check_ban(handler, event, data):
    """Middleware для проверки бана"""
    user_id = event.from_user.id if hasattr(event, 'from_user') else None

    if user_id and await db.is_banned(user_id):
        if isinstance(event, Message):
            await event.answer(
                "🚫 <b>Вы заблокированы</b>\n\n"
                "Если вы считаете, что это ошибка, свяжитесь с администратором.",
                reply_markup=get_contact_admin_keyboard()
            )
        return

    return await handler(event, data)


# ==================== КОМАНДЫ ====================

# /start команда вынесена в handlers/core.py
# /admin команда вынесена в handlers/core.py
# Настройки вынесены в handlers/monitoring.py (settings_menu)
