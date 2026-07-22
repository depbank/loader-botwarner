"""
Главный файл запуска бота — Loader v2.0
Поддерживает: Polling (по умолчанию), Webhook (опционально)
FSM: Redis (если доступен) или MemoryStorage (fallback)
"""
import asyncio
import logging
import sys
import os

# Фикс кодировки для Windows
import utils.encoding_fix

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import config
from database import db
from bot import bot

# Импортируем роутеры
from handlers import features, admin, monitoring
from handlers.core import router as core_router
from handlers.features_stats import router as stats_router
from handlers.tickets import router as tickets_router
from handlers.spam_and_monitoring import router as spam_router, spam_protection
from handlers.custom_design import router as design_router

logger = logging.getLogger(__name__)


# Общий middleware для анти-спама
async def spam_middleware(handler, event, data):
    if hasattr(event, 'from_user') and event.from_user:
        is_spam = await spam_protection.check_spam(event.from_user.id)
        if is_spam:
            if isinstance(event, Message) and event.text:
                await event.answer("⚠️ <b>Не спамьте!</b> Пожалуйста, замедлитесь.")
            return
    return await handler(event, data)


# ==================== FSM STORAGE (Redis fallback) ====================

async def setup_storage():
    """
    Настройка FSM storage.
    Пытается подключиться к Redis, если REDIS_ENABLED=true.
    При ошибке — fallback на MemoryStorage.
    """
    if not config.REDIS_ENABLED:
        logger.info("📝 Использую MemoryStorage (REDIS_ENABLED=false)")
        return MemoryStorage()

    try:
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis as AsyncRedis

        redis_client = AsyncRedis.from_url(config.REDIS_URL)
        await redis_client.ping()
        storage = RedisStorage(redis=redis_client)
        logger.info(f"✅ RedisStorage подключен: {config.REDIS_URL}")
        return storage
    except Exception as e:
        logger.warning(f"⚠️ Redis недоступен ({e}). Использую MemoryStorage.")
        return MemoryStorage()


# ==================== SCHEDULED BROADCAST WORKER ====================

async def scheduled_broadcast_worker():
    """Фоновый планировщик отложенных рассылок"""
    while True:
        try:
            pending = await db.get_pending_scheduled_messages()
            for msg in pending:
                try:
                    users = await db.get_filtered_users(msg['filter_type'])
                    tasks = []
                    for user in users:
                        if user.get('is_banned') and msg['filter_type'] != 'banned':
                            continue
                        tasks.append(_safe_send(user['user_id'], msg['message_text']))

                    results = await asyncio.gather(*tasks)
                    sent = sum(1 for r in results if r)
                    failed = len(results) - sent
                    await db.mark_scheduled_sent(msg['id'], sent, failed)
                    logger.info(f"Scheduled broadcast #{msg['id']} sent: {sent} ok, {failed} failed")
                except Exception as e:
                    logger.error(f"Scheduled broadcast #{msg['id']} error: {e}")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        await asyncio.sleep(30)


async def _safe_send(user_id: int, text: str) -> bool:
    """Безопасная отправка сообщения"""
    try:
        await bot.send_message(user_id, text)
        return True
    except:
        return False


# ==================== STARTUP ====================

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Инициализация базы данных...")
    await db.init_db()
    await db.init_scheduled_table()
    logger.info("База данных готова!")

    # Запускаем фоновые задачи
    asyncio.create_task(features.cleanup_temp_files())
    asyncio.create_task(scheduled_broadcast_worker())
    logger.info("Фоновые задачи запущены")


# ==================== MAIN ENTRY POINT ====================

async def start_polling():
    """Запуск в режиме Polling"""
    from bot import check_maintenance, check_ban

    # Настройка FSM storage
    storage = await setup_storage()
    dp = Dispatcher(storage=storage)

    # Регистрируем все роутеры
    dp.include_router(features.router)
    dp.include_router(admin.router)
    dp.include_router(monitoring.router)
    dp.include_router(core_router)
    dp.include_router(stats_router)
    dp.include_router(tickets_router)
    dp.include_router(spam_router)
    dp.include_router(design_router)

    # Middleware — на каждый роутер
    for r in [features.router, admin.router, monitoring.router, core_router,
              stats_router, tickets_router, spam_router, design_router]:
        r.message.middleware(check_ban)
        r.message.middleware(check_maintenance)
        r.message.middleware(spam_middleware)

    logger.info("🚀 Запуск бота (Polling)...")

    try:
        await on_startup()
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    finally:
        await bot.session.close()
        logger.info("✅ Сессия бота закрыта")


async def start_webhook():
    """Запуск в режиме Webhook (через FastAPI)"""
    from bot import check_maintenance, check_ban
    from aiogram.types import Update

    # Настройка FSM storage
    storage = await setup_storage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры
    dp.include_router(features.router)
    dp.include_router(admin.router)
    dp.include_router(monitoring.router)
    dp.include_router(core_router)
    dp.include_router(stats_router)
    dp.include_router(tickets_router)
    dp.include_router(spam_router)
    dp.include_router(design_router)

    # Middleware
    for r in [features.router, admin.router, monitoring.router, core_router,
              stats_router, tickets_router, spam_router, design_router]:
        r.message.middleware(check_ban)
        r.message.middleware(check_maintenance)
        r.message.middleware(spam_middleware)

    try:
        from fastapi import FastAPI, Request, HTTPException, status
        import secrets
        import uvicorn

        app = FastAPI(title="Loader Bot Webhook")

        @app.on_event("startup")
        async def on_startup_webhook():
            await on_startup()
            webhook_url = config.WEBHOOK_URL
            await bot.set_webhook(
                url=webhook_url,
                secret_token=config.WEBHOOK_SECRET,
                allowed_updates=dp.resolve_used_update_types()
            )
            logger.info(f"✅ Webhook установлен: {webhook_url}")

        @app.on_event("shutdown")
        async def on_shutdown_webhook():
            await bot.delete_webhook()
            await bot.session.close()
            logger.info("👋 Webhook удален, сессия закрыта")

        @app.post(config.WEBHOOK_PATH)
        async def webhook_handler(request: Request):
            secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if not secrets.compare_digest(secret, config.WEBHOOK_SECRET):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

            payload = await request.json()
            update = Update.model_validate(payload)
            await dp.feed_update(bot, update)
            return {"status": "ok"}

        @app.get("/health")
        async def health():
            return {"status": "ok", "bot": "running"}

        logger.info(f"🚀 Запуск бота (Webhook) на порту {config.WEBHOOK_PORT}...")
        config_uvicorn = uvicorn.Config(app, host="0.0.0.0", port=config.WEBHOOK_PORT, log_level="info")
        server = uvicorn.Server(config_uvicorn)
        await server.serve()

    except ImportError as e:
        logger.error(f"❌ FastAPI/uvicorn не установлены: {e}")
        logger.info("↩️ Переключаюсь на Polling...")
        await start_polling()
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        logger.info("↩️ Переключаюсь на Polling...")
        await start_polling()


async def main():
    """Главная функция — выбор режима запуска"""
    if config.USE_WEBHOOK:
        logger.info("🌐 Режим: WEBHOOK")
        await start_webhook()
    else:
        logger.info("🔄 Режим: POLLING")
        await start_polling()


if __name__ == "__main__":
    asyncio.run(main())
