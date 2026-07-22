"""
Тикеты поддержки
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import bot, logger
from database import db
from handlers.spam_and_monitoring import notify_admin_new_ticket
from keyboards import *
import config

router = Router()


@router.message(F.text == "💬 Поддержка")
async def support_ticket(message: Message, state: FSMContext):
    await message.answer(
        "💬 <b>Напишите ваше сообщение:</b>\n\n"
        "Опишите вашу проблему или вопрос.\n"
        "Администратор ответит в ближайшее время.",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state("waiting_for_ticket_message")


@router.message(state="waiting_for_ticket_message")
async def process_ticket_message(message: Message, state: FSMContext):
    if len(message.text) > 4000:
        await message.answer("❌ Сообщение слишком длинное (макс. 4000 символов).")
        return

    try:
        ticket_id = await db.create_ticket(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.text
        )

        await message.answer(
            f"✅ <b>Тикет #{ticket_id} создан!</b>\n\n"
            f"Администратор рассмотрит ваше обращение в ближайшее время.\n"
            f"Вы получите уведомление, когда тикет будет обработан.",
            reply_markup=get_main_menu(is_admin=False)
        )
        await state.clear()

        # Уведомить админа
        await notify_admin_new_ticket(ticket_id, message.from_user)

    except Exception as e:
        logger.error(f"Ticket creation error: {e}")
        await message.answer("❌ Ошибка при создании тикета. Попробуйте позже.")


# ==================== АДМИНКА ТИКЕТОВ ====================

@router.message(F.text == "📋 Тикеты")
async def admin_tickets(message: Message):
    await message.answer("📋 <b>Тикеты поддержки</b>", reply_markup=get_admin_tickets_menu())


@router.callback_query(F.data == "tickets_open_list")
async def tickets_open_list(callback: CallbackQuery):
    tickets = await db.get_open_tickets()
    if not tickets:
        await callback.message.edit_text("✅ Нет открытых тикетов.", reply_markup=get_back_keyboard())
        await callback.answer()
        return

    text = "📋 <b>Открытые тикеты</b>\n\n"
    for ticket in tickets[:10]:
        name = ticket.get('first_name') or 'Unknown'
        text += (
            f"#{ticket['id']} - {name}\n"
            f"📝 {ticket['message'][:50]}...\n\n"
        )

    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("ticket_view_"))
async def ticket_view(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[2])
    ticket = await db.get_ticket(ticket_id)
    if not ticket:
        await callback.message.edit_text("❌ Тикет не найден.", reply_markup=get_back_keyboard())
        await callback.answer()
        return

    text = (
        f"📋 <b>Тикет #{ticket['id']}</b>\n\n"
        f"👤 От: {ticket.get('first_name', 'Unknown')}\n"
        f"🆔 ID: {ticket['user_id']}\n"
        f"📅 Создан: {ticket['created_at']}\n"
        f"📊 Статус: {'🟢 Открыт' if ticket['status'] == 'open' else '🔴 Закрыт'}\n\n"
        f"<b>Сообщение:</b>\n{ticket['message']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_ticket_action_keyboard(ticket_id, ticket['status'])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ticket_close_"))
async def ticket_close(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[2])
    await db.close_ticket(ticket_id)

    await callback.message.edit_text(
        f"✅ Тикет #{ticket_id} закрыт.",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()
