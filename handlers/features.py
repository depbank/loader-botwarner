"""
Обработчики основных функций бота
"""
import os
import time
import asyncio
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot import bot, logger, UserStates
from database import db
from keyboards import *
from utils.qr_generator import generate_qr
from utils.ascii_converter import image_to_ascii
from utils.video_converter import convert_to_round_video, get_video_duration
from utils.social_downloader import downloader
import config

router = Router()


# ==================== HELP & CONTACT ====================

@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    await message.answer(
        "📖 <b>Помощь по использованию бота</b>\n\n"
        "🎨 <b>ASCII Art:</b> Фото → Символы\n"
        "⭕ <b>Video → Round:</b> Видео → Кружочек\n"
        "📥 <b>Social Downloader:</b> Скачивание видео (TT, Insta, YouTube)\n"
        "📊 <b>QR Generator:</b> Текст → QR-код",
        reply_markup=get_contact_admin_keyboard()
    )


@router.message(F.text == "📞 Контакт")
async def show_contact(message: Message):
    await message.answer(
        "📞 <b>Связь с администратором</b>\n\n"
        "Нажмите кнопку ниже, чтобы написать админу.",
        reply_markup=get_contact_admin_keyboard()
    )


# ==================== SOCIAL DOWNLOADER ====================

@router.message(F.text == "📥 Social Downloader")
async def social_downloader_menu(message: Message, state: FSMContext):
    await message.answer(
        "📥 <b>Social Media Downloader</b>\n\n"
        "Отправьте ссылку на видео (TikTok, Instagram, YouTube):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(UserStates.waiting_for_download_url)


@router.message(UserStates.waiting_for_download_url)
async def process_social_download(message: Message, state: FSMContext):
    url = message.text
    if not downloader.is_supported_url(url):
        await message.answer("❌ Ссылка не поддерживается.")
        return

    info = await downloader.get_video_info(url)

    loading_msg = await message.answer("⏳ <b>Инициализация...</b>")

    animations = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]

    async def animate():
        index = 0
        elapsed = 0
        while True:
            try:
                elapsed += 1.5
                percent = min(99, int((elapsed / 60) * 100))
                bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
                await loading_msg.edit_text(
                    f"<b>{animations[index]} Скачивание...</b>\n\n"
                    f"<code>[{bar}] {percent}%</code>\n"
                    f"⏱ Прошло: {int(elapsed)}с"
                )
                index = (index + 1) % len(animations)
                await asyncio.sleep(1.5)
            except:
                break

    anim_task = asyncio.create_task(animate())

    try:
        output_template = os.path.join(config.DOWNLOADS_DIR, f"dl_{message.from_user.id}_%(epoch)s.%(ext)s")
        download_info = await downloader.download(url, output_template)
        anim_task.cancel()

        await db.log_function_use(message.from_user.id, 'downloader')

        actual_path = download_info['filepath']
        if os.path.exists(actual_path):
            await loading_msg.edit_text("📤 <b>Отправка...</b>")
            await message.answer_video(FSInputFile(actual_path), caption=f"✅ {download_info['title']}")
            await loading_msg.delete()
            os.remove(actual_path)
            await state.clear()
        else:
            await loading_msg.edit_text("❌ Файл не найден.")
    except Exception as e:
        if not anim_task.done():
            anim_task.cancel()
        await loading_msg.edit_text(f"❌ Ошибка: {str(e)}")


# ==================== VIDEO TO ROUND ====================

@router.message(F.text == "⭕ Video → Round")
async def video_to_round_menu(message: Message, state: FSMContext):
    await message.answer("⭕ Отправьте видео (до 15 сек) для кружочка:")
    await state.set_state(UserStates.waiting_for_round_video)


@router.message(UserStates.waiting_for_round_video, F.video | F.video_note)
async def handle_round_video(message: Message, state: FSMContext):
    video = message.video or message.video_note
    loading_msg = await message.answer("⏳ <b>Обработка...</b>")

    try:
        file_info = await bot.get_file(video.file_id)
        input_path = os.path.join(config.TEMP_DIR, f"in_{message.from_user.id}.mp4")
        output_path = os.path.join(config.TEMP_DIR, f"round_{message.from_user.id}.mp4")

        await bot.download_file(file_info.file_path, input_path)
        await convert_to_round_video(input_path, output_path)

        await message.answer_video_note(FSInputFile(output_path))
        await loading_msg.delete()

        await db.log_function_use(message.from_user.id, 'video_round')

        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        await state.clear()
    except Exception as e:
        await loading_msg.edit_text(f"❌ Ошибка: {str(e)}")


# ==================== ASCII ART ====================

@router.message(F.text == "🎨 ASCII Art")
async def ascii_menu(message: Message):
    await message.answer("🎨 Отправьте фото для ASCII:")


@router.message(F.photo)
async def handle_photo(message: Message):
    msg = await message.answer("⏳ <b>Генерация ASCII...</b>")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        path = os.path.join(config.TEMP_DIR, f"ascii_{message.from_user.id}.jpg")
        await bot.download_file(file_info.file_path, path)

        ascii_text = await image_to_ascii(path)

        await db.log_function_use(message.from_user.id, 'ascii')

        if len(ascii_text) < 4000:
            await message.answer(f"<code>{ascii_text}</code>")
        else:
            txt_path = path + ".txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(ascii_text)
            await message.answer_document(FSInputFile(txt_path))
            os.remove(txt_path)

        await msg.delete()
        os.remove(path)
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {str(e)}")


# ==================== QR ====================

@router.message(F.text == "📊 QR Generator")
async def qr_menu(message: Message, state: FSMContext):
    await message.answer("📊 Введите текст для QR:")
    await state.set_state(UserStates.waiting_for_qr_text)


@router.message(UserStates.waiting_for_qr_text)
async def handle_qr(message: Message, state: FSMContext):
    try:
        qr_img = await generate_qr(message.text)
        await message.answer_photo(BufferedInputFile(qr_img.read(), filename="qr.png"))
        await db.log_function_use(message.from_user.id, 'qr')
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


async def cleanup_temp_files():
    """Фоновая очистка временных файлов"""
    while True:
        await asyncio.sleep(3600)
        try:
            now = time.time()
            for f in os.listdir(config.TEMP_DIR):
                file_path = os.path.join(config.TEMP_DIR, f)
                if os.path.isfile(file_path):
                    age = now - os.path.getmtime(file_path)
                    if age > 3600:
                        os.remove(file_path)
        except:
            pass
