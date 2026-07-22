"""
Спам и мониторинг + уведомления админов
"""
import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import bot, logger, AdminStates
from database import db
from keyboards import *
import config

router = Router()


# ==================== SPAM PROTECTION ====================

class SpamProtection:
    def __init__(self):
        self.user_messages = {}

    async def check_spam(self, user_id: int) -> bool:
        """Проверка на спам (не более N сообщений в секунду)"""
        recent = await db.get_recent_spam_actions(user_id, seconds=3)
        if recent > 5:
            await db.log_spam_action(user_id, 'blocked')
            return True
        await db.log_spam_action(user_id, 'allowed')
        return False


spam_protection = SpamProtection()


# ==================== УВЕДОМЛЕНИЯ АДМИНАМ ====================

async def notify_new_user(user_id: int, name: str):
    """Уведомить админа о новом пользователе"""
    try:
        await bot.send_message(
            config.MAIN_ADMIN_ID,
            f"🆕 <b>Новый пользователь!</b>\n\n"
            f"👤 Имя: {name}\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"📅 Время: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}"
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def notify_admin_new_ticket(ticket_id: int, user):
    """Уведомить админа о новом тикете"""
    try:
        await bot.send_message(
            config.MAIN_ADMIN_ID,
            f"📋 <b>Новый тикет #{ticket_id}</b>\n\n"
            f"👤 От: {user.first_name or 'Unknown'}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📝 <code>{__import__('datetime').datetime.now().strftime('%H:%M:%S')}</code>"
        )
    except Exception as e:
        logger.error(f"Failed to notify admin about ticket: {e}")


# ==================== АНТИ-СПАМ МЕНЮ ====================

@router.message(F.text == "🛡️ Анти-спам")
async def spam_menu(message: Message):
    await message.answer("🛡️ <b>Анти-спам</b>", reply_markup=get_spam_settings_menu())
