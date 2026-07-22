"""
Цветные кнопки для Telegram Bot API 9.4+
Поддержка style: primary (синий), danger (красный), success (зелёный)
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from typing import Optional, List, Union


def colored_inline_button(
    text: str,
    callback_data: Optional[str] = None,
    url: Optional[str] = None,
    style: str = "primary",
    emoji_id: Optional[str] = None
) -> InlineKeyboardButton:
    kwargs = {
        "text": text,
        "style": style,
    }
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = emoji_id
    return InlineKeyboardButton(**kwargs)


def colored_inline_markup(
    buttons: List[List[dict]],
    resize_keyboard: bool = True
) -> InlineKeyboardMarkup:
    keyboard = []
    for row in buttons:
        row_buttons = []
        for btn_data in row:
            kwargs = {
                "text": btn_data["text"],
                "style": btn_data.get("style", "primary"),
            }
            if "callback_data" in btn_data:
                kwargs["callback_data"] = btn_data["callback_data"]
            if "url" in btn_data:
                kwargs["url"] = btn_data["url"]
            if "emoji_id" in btn_data:
                kwargs["icon_custom_emoji_id"] = btn_data["emoji_id"]
            row_buttons.append(InlineKeyboardButton(**kwargs))
        keyboard.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def colored_reply_button(
    text: str,
    style: str = "primary",
    emoji_id: Optional[str] = None
) -> KeyboardButton:
    kwargs = {
        "text": text,
        "style": style,
    }
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = emoji_id
    return KeyboardButton(**kwargs)


def colored_reply_markup(
    buttons: List[List[dict]],
    resize_keyboard: bool = True,
    one_time_keyboard: bool = False
) -> ReplyKeyboardMarkup:
    keyboard = []
    for row in buttons:
        row_buttons = []
        for btn_data in row:
            kwargs = {
                "text": btn_data["text"],
                "style": btn_data.get("style", "primary"),
            }
            if "emoji_id" in btn_data:
                kwargs["icon_custom_emoji_id"] = btn_data["emoji_id"]
            row_buttons.append(KeyboardButton(**kwargs))
        keyboard.append(row_buttons)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard
    )
