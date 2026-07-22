"""
Обработчики мониторинга
"""
import os
import sys
import psutil
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime
import io

from bot import bot, logger, AdminStates
from database import db
from keyboards import *
import config

router = Router()


# ==================== ВХОД В МОНИТОРИНГ ====================

@router.message(F.text == "📊 Мониторинг")
async def monitoring_menu(message: Message, state: FSMContext):
    if message.from_user.id == config.MAIN_ADMIN_ID:
        await message.answer("📊 <b>Мониторинг сервера</b>", reply_markup=get_monitoring_menu())
    else:
        await message.answer("🔐 <b>Введите пароль мониторинга:</b>", reply_markup=get_cancel_keyboard())
        await state.set_state(AdminStates.waiting_for_monitoring_password)


@router.message(AdminStates.waiting_for_monitoring_password)
async def process_monitoring_password(message: Message, state: FSMContext):
    password = await db.get_setting('monitoring_password') or config.MONITORING_PASSWORD
    if message.text.strip() == password:
        await message.answer("✅ <b>Пароль верный!</b>", reply_markup=get_monitoring_menu())
        await state.clear()
    else:
        await message.answer("❌ <b>Неверный пароль!</b>", reply_markup=get_cancel_keyboard())


# ==================== ТЕКУЩАЯ НАГРУЗКА ====================

@router.callback_query(F.data == "monitor_current")
async def monitor_current(callback: CallbackQuery):
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    cpu_str = f"{'🟢' if cpu < 50 else '🟡' if cpu < 80 else '🔴'} {cpu}%"
    mem_str = f"{'🟢' if memory.percent < 50 else '🟡' if memory.percent < 80 else '🔴'} {memory.percent}%"
    disk_str = f"{'🟢' if disk.percent < 50 else '🟡' if disk.percent < 80 else '🔴'} {disk.percent}%"

    text = (
        f"📊 <b>Текущая нагрузка</b>\n\n"
        f"🖥 CPU: {cpu_str}\n"
        f"💾 RAM: {mem_str}\n"
        f"💿 Диск: {disk_str}\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "monitor_info")
async def monitor_info(callback: CallbackQuery):
    import platform
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    text = (
        f"ℹ️ <b>Информация о сервере</b>\n\n"
        f"🖥 Система: {platform.system()} {platform.release()}\n"
        f"🐍 Python: {sys.version.split()[0]}\n"
        f"⏱ Uptime: {days}д {hours}ч {minutes}м\n"
        f"📅 Запущен: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📂 Процессов: {len(psutil.pids())}"
    )

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()
