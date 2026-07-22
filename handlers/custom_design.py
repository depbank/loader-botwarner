"""
Кастомный дизайн — настройка приветствия, цветов, темы
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import AdminStates
from database import db
from keyboards import *
import config

router = Router()


@router.message(F.text == "🎨 Дизайн")
async def design_menu(message: Message):
    await message.answer("🎨 <b>Настройки дизайна</b>", reply_markup=get_design_menu())


@router.callback_query(F.data == "design_menu")
async def design_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text("🎨 <b>Настройки дизайна</b>", reply_markup=get_design_menu())
    await callback.answer()


@router.callback_query(F.data == "design_welcome")
async def design_welcome(callback: CallbackQuery, state: FSMContext):
    current = await db.get_design_setting('welcome_text') or 'Не установлено'
    await callback.message.edit_text(
        f"📝 <b>Текст приветствия</b>\n\n"
        f"Текущий:\n<code>{current[:200]}</code>\n\n"
        f"Отправьте новый текст (используйте {'{name}'} для имени):\n"
        f"Или нажмите кнопку ниже для сброса.",
        reply_markup=colored_inline_markup([
            [{"text": "🔄 Сбросить", "callback_data": "design_reset_welcome", "style": "danger"}],
            [{"text": "🔙 Назад", "callback_data": "design_menu", "style": "primary"}]
        ])
    )
    await state.set_state(AdminStates.waiting_for_welcome_text)
    await callback.answer()


@router.callback_query(F.data == "design_reset_welcome")
async def design_reset_welcome(callback: CallbackQuery):
    await db.set_design_setting('welcome_text',
        '👋 <b>Привет, {name}!</b>\n\nЯ многофункциональный бот с крутыми возможностями')
    await callback.message.edit_text("✅ Текст приветствия сброшен!", reply_markup=get_design_menu())
    await callback.answer()


@router.message(AdminStates.waiting_for_welcome_text)
async def design_set_welcome(message: Message, state: FSMContext):
    await db.set_design_setting('welcome_text', message.text)
    await message.answer("✅ Текст приветствия сохранен!", reply_markup=get_design_menu())
    await state.clear()


@router.callback_query(F.data == "design_button_color")
async def design_button_color(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎨 <b>Выберите цвет кнопок:</b>",
        reply_markup=get_color_choice_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("design_set_color_"))
async def design_set_color(callback: CallbackQuery):
    color = callback.data.split("_")[3]
    await db.set_design_setting('button_color', color)
    await callback.message.edit_text(f"✅ Цвет кнопок изменен на {color}!", reply_markup=get_design_menu())
    await callback.answer()


@router.callback_query(F.data == "design_theme")
async def design_theme(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌓 <b>Выберите тему:</b>",
        reply_markup=get_theme_choice_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("design_set_theme_"))
async def design_set_theme(callback: CallbackQuery):
    theme = callback.data.split("_")[3]
    await db.set_design_setting('theme', theme)
    await callback.message.edit_text(f"✅ Тема изменена на {theme}!", reply_markup=get_design_menu())
    await callback.answer()
