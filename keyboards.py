"""
ВСЕ КНОПКИ ЦВЕТНЫЕ — Telegram Bot API 9.4+
Ни одной серой кнопки!
style legend: primary=синий, success=зелёный, danger=красный
"""

from utils.colored_keyboards import colored_reply_markup, colored_inline_markup


# ==================== REPLY КЛАВИАТУРЫ (ЦВЕТНЫЕ) ====================

def get_main_menu(is_admin=False):
    """Главное меню — цветные кнопки"""
    buttons = [
        [
            {"text": "🎨 ASCII Art", "style": "primary"},
            {"text": "⭕ Video → Round", "style": "primary"}
        ],
        [
            {"text": "📥 Social Downloader", "style": "primary"},
            {"text": "📊 QR Generator", "style": "primary"}
        ],
    ]

    if is_admin:
        buttons.append([
            {"text": "👨‍💼 Админ-панель", "style": "success"},
            {"text": "ℹ️ Помощь", "style": "primary"}
        ])
    else:
        buttons.append([
            {"text": "ℹ️ Помощь", "style": "primary"},
            {"text": "💬 Поддержка", "style": "success"}
        ])

    return colored_reply_markup(buttons)


def get_admin_menu():
    """Меню администратора"""
    buttons = [
        [
            {"text": "👥 Пользователи", "style": "primary"},
            {"text": "👨‍💼 Админы", "style": "danger"}
        ],
        [
            {"text": "📊 Статистика функций", "style": "success"},
            {"text": "🏆 Топ пользователей", "style": "primary"}
        ],
        [
            {"text": "🔍 Поиск юзера", "style": "primary"},
            {"text": "📋 UCP-панель", "style": "success"}
        ],
        [
            {"text": "📢 Рассылка", "style": "primary"},
            {"text": "📅 Отложенная", "style": "success"}
        ],
        [
            {"text": "🔧 Режим ТО", "style": "danger"},
            {"text": "📋 Тикеты", "style": "primary"}
        ],
        [
            {"text": "🛡️ Анти-спам", "style": "danger"},
            {"text": "📊 Мониторинг", "style": "success"}
        ],
        [
            {"text": "📝 Логи", "style": "primary"},
            {"text": "🌐 Статус серверов", "style": "primary"}
        ],
        [
            {"text": "🔔 Настройки уведомлений", "style": "success"},
            {"text": "🎨 Дизайн", "style": "primary"}
        ],
        [
            {"text": "⚙️ Настройки", "style": "success"},
            {"text": "🔙 В главное меню", "style": "danger"}
        ]
    ]

    return colored_reply_markup(buttons)


# ==================== INLINE КЛАВИАТУРЫ (ЦВЕТНЫЕ) ====================

def get_ascii_output_type():
    """Выбор типа вывода ASCII"""
    return colored_inline_markup([
        [
            {"text": "📄 Файл", "callback_data": "ascii_file", "style": "primary"},
            {"text": "💬 Текст", "callback_data": "ascii_text", "style": "success"}
        ],
        [
            {"text": "🎥 Видео", "callback_data": "ascii_video", "style": "danger"}
        ]
    ])


def get_users_menu(page=0):
    """Меню управления пользователями"""
    return colored_inline_markup([
        [
            {"text": "📊 Статистика", "callback_data": "users_stats", "style": "success"}
        ],
        [
            {"text": "📋 Список пользователей", "callback_data": f"users_list_{page}", "style": "primary"}
        ],
        [
            {"text": "🚫 Бан/Разбан", "callback_data": "users_ban", "style": "danger"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_admins_menu():
    """Меню управления админами"""
    return colored_inline_markup([
        [
            {"text": "➕ Добавить админа", "callback_data": "admin_add", "style": "success"}
        ],
        [
            {"text": "➖ Удалить админа", "callback_data": "admin_remove", "style": "danger"}
        ],
        [
            {"text": "📋 Список админов", "callback_data": "admin_list", "style": "primary"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_broadcast_menu():
    """Меню рассылки"""
    return colored_inline_markup([
        [
            {"text": "📢 Всем пользователям", "callback_data": "broadcast_all", "style": "primary"}
        ],
        [
            {"text": "👤 Конкретному пользователю", "callback_data": "broadcast_user", "style": "success"}
        ],
        [
            {"text": "🎯 С фильтром", "callback_data": "broadcast_filtered", "style": "primary"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_maintenance_menu(is_active=False):
    """Меню режима техобслуживания"""
    status_text = "✅ Включен" if is_active else "❌ Выключен"
    toggle_text = "🔴 Выключить" if is_active else "🟢 Включить"
    toggle_callback = "maintenance_off" if is_active else "maintenance_on"
    toggle_style = "danger" if is_active else "success"

    return colored_inline_markup([
        [
            {"text": f"Статус: {status_text}", "callback_data": "maintenance_status", "style": "primary"}
        ],
        [
            {"text": toggle_text, "callback_data": toggle_callback, "style": toggle_style}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_monitoring_menu():
    """Меню мониторинга"""
    return colored_inline_markup([
        [
            {"text": "📊 Текущая нагрузка", "callback_data": "monitor_current", "style": "success"}
        ],
        [
            {"text": "📈 Получить график", "callback_data": "monitor_graph", "style": "primary"}
        ],
        [
            {"text": "ℹ️ Информация о сервере", "callback_data": "monitor_info", "style": "primary"}
        ],
        [
            {"text": "🔄 Перезагрузить бота", "callback_data": "monitor_restart", "style": "danger"}
        ],
        [
            {"text": "🔴 ВЫКЛЮЧИТЬ СЕРВЕР", "callback_data": "monitor_shutdown", "style": "danger"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_logs_menu():
    """Меню логов"""
    return colored_inline_markup([
        [
            {"text": "📜 Все логи", "callback_data": "logs_all", "style": "primary"}
        ],
        [
            {"text": "👤 Логи пользователя", "callback_data": "logs_user", "style": "success"}
        ],
        [
            {"text": "👨‍💼 Логи админа", "callback_data": "logs_admin", "style": "primary"}
        ],
        [
            {"text": "🗑️ Очистить логи", "callback_data": "logs_clear", "style": "danger"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_settings_menu():
    """Меню настроек"""
    return colored_inline_markup([
        [
            {"text": "🔑 Сменить пароль админки", "callback_data": "settings_admin_pass", "style": "success"}
        ],
        [
            {"text": "🔐 Сменить пароль мониторинга", "callback_data": "settings_monitor_pass", "style": "primary"}
        ],
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_confirmation_keyboard(action: str):
    """Клавиатура подтверждения"""
    return colored_inline_markup([
        [
            {"text": "✅ Да", "callback_data": f"confirm_{action}", "style": "success"},
            {"text": "❌ Нет", "callback_data": f"cancel_{action}", "style": "danger"}
        ]
    ])


def get_contact_admin_keyboard():
    """Кнопка связи с админом"""
    import config
    return colored_inline_markup([
        [
            {"text": "✉️ Написать админу", "url": f"tg://user?id={config.MAIN_ADMIN_ID}", "style": "primary"}
        ]
    ])


def get_cancel_keyboard():
    """Кнопка отмены"""
    return colored_inline_markup([
        [
            {"text": "❌ Отмена", "callback_data": "cancel", "style": "danger"}
        ]
    ])


def get_back_keyboard():
    """Кнопка назад"""
    return colored_inline_markup([
        [
            {"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}
        ]
    ])


def get_stats_menu():
    """Меню статистики"""
    return colored_inline_markup([
        [{"text": "📊 Общая статистика", "callback_data": "stats_overview", "style": "success"}],
        [{"text": "🏆 Топ пользователей", "callback_data": "stats_top_users", "style": "primary"}],
        [{"text": "📦 Экспорт в CSV", "callback_data": "stats_export", "style": "success"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_admin_tickets_menu():
    """Меню тикетов для админа"""
    return colored_inline_markup([
        [{"text": "📋 Список открытых тикетов", "callback_data": "tickets_open_list", "style": "primary"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_ticket_admin_keyboard(ticket_id: int):
    """Клавиатура для тикета (для админа)"""
    return colored_inline_markup([
        [{"text": "👁️ Просмотр", "callback_data": f"ticket_view_{ticket_id}", "style": "primary"}],
        [{"text": "✅ Закрыть", "callback_data": f"ticket_close_{ticket_id}", "style": "danger"}]
    ])


def get_ticket_action_keyboard(ticket_id: int, status: str):
    """Клавиатура действий с тикетом"""
    buttons = []
    if status == 'open':
        buttons.append([{"text": "✅ Закрыть тикет", "callback_data": f"ticket_close_{ticket_id}", "style": "danger"}])
    buttons.append([{"text": "🔙 Назад", "callback_data": "tickets_open_list", "style": "primary"}])
    return colored_inline_markup(buttons)


def get_design_menu():
    """Меню дизайна"""
    return colored_inline_markup([
        [{"text": "📝 Текст приветствия", "callback_data": "design_welcome", "style": "success"}],
        [{"text": "🎨 Цвет кнопок", "callback_data": "design_button_color", "style": "primary"}],
        [{"text": "🌓 Тема", "callback_data": "design_theme", "style": "primary"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_color_choice_keyboard():
    """Выбор цвета"""
    return colored_inline_markup([
        [{"text": "🔵 Синий (primary)", "callback_data": "design_set_color_primary", "style": "primary"}],
        [{"text": "🟢 Зелёный (success)", "callback_data": "design_set_color_success", "style": "success"}],
        [{"text": "🔴 Красный (danger)", "callback_data": "design_set_color_danger", "style": "danger"}],
        [{"text": "🔙 Назад", "callback_data": "design_menu", "style": "primary"}]
    ])


def get_theme_choice_keyboard():
    """Выбор темы"""
    return colored_inline_markup([
        [{"text": "🌙 Тёмная", "callback_data": "design_set_theme_dark", "style": "primary"}],
        [{"text": "☀️ Светлая", "callback_data": "design_set_theme_light", "style": "success"}],
        [{"text": "🔙 Назад", "callback_data": "design_menu", "style": "primary"}]
    ])


def get_notification_settings_menu():
    """Меню уведомлений"""
    return colored_inline_markup([
        [{"text": "👤 Новые пользователи", "callback_data": "notify_toggle_users", "style": "success"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_server_status_menu():
    """Меню статуса серверов"""
    return colored_inline_markup([
        [{"text": "➕ Добавить сервер", "callback_data": "server_add", "style": "success"}],
        [{"text": "🔄 Проверить все", "callback_data": "server_check_all", "style": "primary"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_spam_settings_menu():
    """Меню анти-спама"""
    return colored_inline_markup([
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


def get_broadcast_filter_menu():
    """Меню выбора фильтра аудитории"""
    return colored_inline_markup([
        [{"text": "👥 Всем пользователям", "callback_data": "sched_filter_all", "style": "primary"}],
        [{"text": "✅ Активным (7д)", "callback_data": "sched_filter_active", "style": "success"}],
        [{"text": "🚫 Забаненным", "callback_data": "sched_filter_banned", "style": "danger"}],
        [{"text": "👑 Администраторам", "callback_data": "sched_filter_admins", "style": "primary"}],
        [{"text": "🔙 Назад", "callback_data": "admin_back", "style": "primary"}]
    ])


__all__ = [
    'get_main_menu', 'get_admin_menu',
    'get_ascii_output_type',
    'get_users_menu', 'get_admins_menu',
    'get_broadcast_menu', 'get_maintenance_menu',
    'get_monitoring_menu', 'get_logs_menu',
    'get_settings_menu', 'get_confirmation_keyboard',
    'get_contact_admin_keyboard', 'get_cancel_keyboard',
    'get_back_keyboard',
    'get_stats_menu', 'get_admin_tickets_menu',
    'get_ticket_admin_keyboard', 'get_ticket_action_keyboard',
    'get_design_menu', 'get_color_choice_keyboard', 'get_theme_choice_keyboard',
    'get_notification_settings_menu', 'get_server_status_menu',
    'get_spam_settings_menu', 'get_broadcast_filter_menu',
]
