"""
Базовые обработчики — кнопки + /start
"""
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot import bot, AdminStates
from database import db
from keyboards import get_main_menu, get_admin_menu, get_cancel_keyboard, get_contact_admin_keyboard
from handlers.spam_and_monitoring import notify_new_user
import config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db.add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )

    welcome_template = await db.get_design_setting('welcome_text')
    if not welcome_template:
        welcome_template = "👋 <b>Привет, {name}!</b>\n\nЯ многофункциональный бот"

    welcome_text = welcome_template.replace('{name}', message.from_user.first_name or 'друг')
    welcome_text += (
        "\n\n🎨 <b>ASCII Art</b> - Фото в символы\n"
        "⭕ <b>Video → Round</b> - Видео в кружочек\n"
        "📥 <b>Social Downloader</b> - Скачивание\n"
        "📊 <b>QR Generator</b> - QR-коды\n"
        "💬 <b>Поддержка</b> - Связаться с админом"
    )

    is_admin = await db.is_admin(message.from_user.id)
    await message.answer(welcome_text, reply_markup=get_main_menu(is_admin=is_admin))

    # Уведомляем админа о новом пользователе
    settings = await db.get_setting('notify_new_user')
    if settings != 'false':
        is_new = await db.get_user(message.from_user.id)
        if is_new and is_new.get('joined_at'):
            from datetime import datetime, timezone
            try:
                reg_time = datetime.strptime(is_new['joined_at'][:19], '%Y-%m-%d %H:%M:%S')
                reg_time = reg_time.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if (now - reg_time).total_seconds() < 30:
                    asyncio.create_task(notify_new_user(message.from_user.id, message.from_user.first_name or 'User'))
            except:
                pass


@router.message(F.text == "🏠 Главная")
async def home_button(message: Message, state: FSMContext):
    await state.clear()
    await db.add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )

    welcome_template = await db.get_design_setting('welcome_text')
    if not welcome_template:
        welcome_template = "👋 <b>Привет, {name}!</b>\n\nЯ многофункциональный бот"

    welcome_text = welcome_template.replace('{name}', message.from_user.first_name or 'друг')
    welcome_text += (
        "\n\n🎨 <b>ASCII Art</b> - Фото в символы\n"
        "⭕ <b>Video → Round</b> - Видео в кружочек\n"
        "📥 <b>Social Downloader</b> - Скачивание\n"
        "📊 <b>QR Generator</b> - QR-коды\n"
        "💬 <b>Поддержка</b> - Связаться с админом"
    )

    is_admin = await db.is_admin(message.from_user.id)
    await message.answer(welcome_text, reply_markup=get_main_menu(is_admin=is_admin))


@router.message(F.text == "👨‍💼 Админ-панель")
async def admin_panel_button(message: Message, state: FSMContext):
    if message.from_user.id == config.MAIN_ADMIN_ID:
        await message.answer("👨‍💼 <b>Админ-панель</b>", reply_markup=get_admin_menu())
    elif await db.is_admin(message.from_user.id):
        await message.answer("🔐 <b>Введите пароль:</b>", reply_markup=get_cancel_keyboard())
        await state.set_state(AdminStates.waiting_for_admin_password)
    else:
        await message.answer("❌ У вас нет прав администратора.")
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu(is_admin=False))
