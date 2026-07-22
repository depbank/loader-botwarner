# DepBank Bot 🤖

[![CI/CD](https://github.com/TAIIENT/depbank/actions/workflows/ci.yml/badge.svg)](https://github.com/TAIIENT/depbank/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Aiogram](https://img.shields.io/badge/aiogram-3.6+-green)](https://docs.aiogram.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **DepBank** — Многофункциональный Telegram бот
  
## Возможности 🚀

| Функция | Описание |
|---------|----------|
| 🎨 **ASCII Art** | Конвертация фото в ASCII-символы |
| ⭕ **Video → Round** | Преобразование видео в кружочек |
| 📥 **Social Downloader** | Скачивание с TikTok, Instagram, YouTube |
| 📊 **QR Generator** | Генерация QR-кодов из текста |
| 💬 **Поддержка** | Система тикетов для пользователей |
| 👨‍💼 **Админ-панель** | Управление пользователями, статистика, рассылки |

## Быстрый старт 🚀

```bash
# 1. Клонировать репозиторий
git clone https://github.com/TAIIENT/depbank.git
cd depbank

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env и заполнить
cp .env.example .env
# Открой .env и вставь BOT_TOKEN и MAIN_ADMIN_ID

# 4. Запустить
python main.py
```

## Docker 🐳

```bash
docker-compose up -d --build
```

## Технологии 🛠

- **Python 3.11+**
- **Aiogram 3.6+** — Фреймворк для Telegram Bot API
- **SQLite (aiosqlite)** — База данных
- **Redis** — FSM storage (опционально)
- **FFmpeg** — Обработка видео
- **yt-dlp** — Скачивание из соцсетей

## Структура проекта 📁

```
depbank/
├── main.py                 # Точка входа
├── bot.py                  # Инициализация бота
├── config.py               # Конфигурация
├── database.py             # База данных
├── keyboards.py            # Кнопки
├── handlers/               # Обработчики команд
│   ├── core.py             # /start, кнопки
│   ├── features.py         # ASCII, QR, Downloader, Video
│   ├── admin.py            # Админ-панель
│   ├── monitoring.py       # Мониторинг системы
│   ├── features_stats.py   # Статистика
│   ├── tickets.py          # Тикеты поддержки
│   ├── spam_and_monitoring.py
│   └── custom_design.py    # Дизайн
├── utils/                  # Утилиты
│   ├── ascii_converter.py
│   ├── qr_generator.py
│   ├── social_downloader.py
│   ├── video_converter.py
│   ├── monitoring.py
│   └── colored_keyboards.py
├── Dockerfile              # Docker
├── docker-compose.yml      # Docker Compose
└── .env.example            # Пример конфига
```

## Безопасность 🔒

- `.env` в `.gitignore` — токен никогда не утечёт
- GitHub Actions проверяет что `.env` не в репозитории
- Redis опционально для FSM Storage

## Бесплатный деплой ☁️

1. Залей код на **[Render.com](https://render.com)** (бесплатно, но спит через 15 мин)
2. Или на **[Railway.app](https://railway.app)** (есть $5 бесплатно)
3. Или на **[PythonAnywhere](https://pythonanywhere.com)** (бесплатный Python)
4. Или свой VPS через докер

## Лицензия 📄

MIT License

---

**Made with AI and ❤️ by [TAIIENT](https://github.com/TAIIENT)**
