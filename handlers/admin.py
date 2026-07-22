"""
Обработчики админ-панели
"""
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import bot, logger, AdminStates
from database import db
from keyboards import *
from utils.colored_keyboards import colored_inline_markup
import config

router = Router()


# ==================== ВХОД В АДМИН-ПАНЕЛЬ ====================

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id == config.MAIN_ADMIN_ID:
        await message.answer("👨‍💼 <b>Админ-панель</b>", reply_markup=get_admin_menu())
    elif await db.is_admin(message.from_user.id):
        await message.answer("🔐 <b>Введите пароль:</b>", reply_markup=get_cancel_keyboard())
        await state.set_state(AdminStates.waiting_for_admin_password)
    else:
        await message.answer("❌ У вас нет прав администратора.")
        is_admin = await db.is_admin(message.from_user.id)
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu(is_admin=False))


@router.message(AdminStates.waiting_for_admin_password)
async def process_admin_password(message: Message, state: FSMContext):
    password = await db.get_setting('admin_password') or config.ADMIN_PASSWORD
    if message.text.strip() == password:
        await message.answer("✅ <b>Пароль верный!</b>", reply_markup=get_admin_menu())
        await state.clear()
    else:
        await message.answer("❌ <b>Неверный пароль!</b> Попробуйте снова:", reply_markup=get_cancel_keyboard())


# ==================== ПОЛЬЗОВАТЕЛИ ====================

@router.message(F.text == "👥 Пользователи")
async def users_menu(message: Message):
    await message.answer("👥 <b>Управление пользователями</b>", reply_markup=get_users_menu())


@router.callback_query(F.data.startswith("users_stats"))
async def users_stats(callback: CallbackQuery):
    stats = await db.get_stats()
    await callback.message.edit_text(
        f"📊 <b>Статистика пользователей</b>\n\n"
        f"👥 Всего: {stats['total_users']}\n"
        f"✅ Активных (7д): {stats['active_users']}\n"
        f"🚫 Забанено: {stats['banned_users']}\n"
        f"📥 Всего скачиваний: {stats['total_downloads']}",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("users_list_"))
async def users_list(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    users = await db.get_all_users()
    if not users:
        await callback.message.edit_text("❌ Нет пользователей.", reply_markup=get_back_keyboard())
        await callback.answer()
        return

    start = page * 10
    end = start + 10
    page_users = users[start:end]

    text = f"📋 <b>Список пользователей</b> (стр. {page + 1})\n\n"
    for user in page_users:
        name = user.get('first_name') or 'Unknown'
        username = f"@{user['username']}" if user.get('username') else ''
        status = "🚫" if user.get('is_banned') else "✅"
        text += f"{status} <code>{user['user_id']}</code> {name} {username}\n"

    nav_buttons = []
    if page > 0:
        nav_buttons.append({"text": "⬅️", "callback_data": f"users_list_{page - 1}", "style": "primary"})
    if end < len(users):
        nav_buttons.append({"text": "➡️", "callback_data": f"users_list_{page + 1}", "style": "primary"})

    buttons = [nav_buttons] if nav_buttons else []
    buttons.append([{"text": "🔙 Назад", "callback_data": "users_menu", "style": "primary"}])

    await callback.message.edit_text(text, reply_markup=colored_inline_markup(buttons))
    await callback.answer()


@router.callback_query(F.data == "users_menu")
async def users_menu_back(callback: CallbackQuery):
    await callback.message.edit_text("👥 <b>Управление пользователями</b>", reply_markup=get_users_menu())
    await callback.answer()
