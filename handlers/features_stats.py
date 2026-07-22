"""
Статистика функций
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
import csv
import io

from database import db
from keyboards import *

router = Router()


@router.message(F.text == "📊 Статистика функций")
async def stats_menu(message: Message):
    await message.answer("📊 <b>Статистика</b>", reply_markup=get_stats_menu())


@router.callback_query(F.data == "stats_overview")
async def stats_overview(callback: CallbackQuery):
    stats = await db.get_stats()
    func_stats = await db.get_function_stats()
    weekly = await db.get_weekly_stats()

    text = (
        f"📊 <b>Общая статистика</b>\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"✅ Активных (7д): {stats['active_users']}\n"
        f"🚫 Забанено: {stats['banned_users']}\n\n"
        f"<b>Использование функций:</b>\n"
        f"🎨 ASCII: {func_stats.get('ascii', 0)}\n"
        f"📊 QR: {func_stats.get('qr', 0)}\n"
        f"📥 Downloader: {func_stats.get('downloader', 0)}\n"
        f"⭕ Video Round: {func_stats.get('video_round', 0)}\n"
        f"📥 Всего скачиваний: {stats['total_downloads']}\n\n"
        f"<b>Активность за неделю:</b>\n"
    )

    if weekly:
        for day, count in sorted(weekly.items()):
            text += f"  {day}: {count} действий\n"
    else:
        text += "  Нет данных за неделю\n"

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "stats_top_users")
async def stats_top_users(callback: CallbackQuery):
    top_users = await db.get_top_users(limit=10)
    if not top_users:
        await callback.message.edit_text("❌ Нет данных об активности.", reply_markup=get_back_keyboard())
        await callback.answer()
        return

    text = "🏆 <b>Топ 10 пользователей</b>\n\n"
    for i, user in enumerate(top_users, 1):
        name = user.get('first_name') or 'Unknown'
        username = f" (@{user['username']})" if user.get('username') else ""
        text += f"{i}. <code>{user['user_id']}</code>{username} - {name}: {user['total_actions']} действий\n"

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data == "stats_export")
async def stats_export(callback: CallbackQuery):
    users = await db.get_all_users()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Banned', 'Joined', 'Last Activity'])

    for user in users:
        writer.writerow([
            user['user_id'],
            user.get('username', ''),
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('is_banned', 0),
            user.get('joined_at', ''),
            user.get('last_activity', '')
        ])

    csv_bytes = output.getvalue().encode('utf-8-sig')
    await callback.message.answer_document(
        BufferedInputFile(csv_bytes, filename="users_export.csv"),
        caption="📦 Экспорт пользователей"
    )
    await callback.answer()
