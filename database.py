import aiosqlite
from datetime import datetime
from typing import Optional, List, Dict
import json
import config


class Database:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_banned INTEGER DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица админов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Таблица истории скачиваний
            await db.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT,
                    download_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Таблица логов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Таблица настроек
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # Таблица статистики функций
            await db.execute("""
                CREATE TABLE IF NOT EXISTS function_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    function_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица тикетов поддержки
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    message TEXT,
                    status TEXT DEFAULT 'open',
                    admin_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица анти-спама
            await db.execute("""
                CREATE TABLE IF NOT EXISTS spam_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица настроек дизайна
            await db.execute("""
                CREATE TABLE IF NOT EXISTS design_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # Таблица мониторинга серверов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS server_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT,
                    server_url TEXT,
                    is_active INTEGER DEFAULT 1,
                    last_status TEXT,
                    last_checked TIMESTAMP
                )
            """)

            # Инициализация настроек по умолчанию
            await db.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES
                ('admin_password', ?),
                ('monitoring_password', ?),
                ('maintenance_mode', 'false'),
                ('maintenance_reason', ''),
                ('maintenance_duration', '')
            """, (config.ADMIN_PASSWORD, config.MONITORING_PASSWORD))

            # Инициализация дизайна по умолчанию
            await db.execute("""
                INSERT OR IGNORE INTO design_settings (key, value) VALUES
                ('welcome_text', '👋 <b>Привет, {name}!</b>\n\nЯ многофункциональный бот с крутыми возможностями'),
                ('button_color', 'primary'),
                ('theme', 'dark'),
                ('admin_welcome', '👨‍💼 <b>Добро пожаловать в админ-панель</b>')
            """)

            await db.commit()

    # ==================== USERS ====================

    async def add_user(self, user_id: int, username: str = None,
                      first_name: str = None, last_name: str = None):
        """Добавить или обновить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    last_activity = CURRENT_TIMESTAMP
            """, (user_id, username, first_name, last_name))
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить информацию о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_users(self) -> List[Dict]:
        """Получить всех пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users ORDER BY joined_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def ban_user(self, user_id: int):
        """Забанить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
            )
            await db.commit()

    async def unban_user(self, user_id: int):
        """Разбанить пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,)
            )
            await db.commit()

    async def is_banned(self, user_id: int) -> bool:
        """Проверить, забанен ли пользователь"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT is_banned FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return bool(row[0]) if row else False

    # ==================== ADMINS ====================

    async def add_admin(self, user_id: int, added_by: int):
        """Добавить админа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
                (user_id, added_by)
            )
            await db.commit()

    async def remove_admin(self, user_id: int):
        """Удалить админа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await db.commit()

    async def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь админом"""
        if user_id == config.MAIN_ADMIN_ID:
            return True

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id FROM admins WHERE user_id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone() is not None

    async def get_all_admins(self) -> List[Dict]:
        """Получить всех админов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT a.user_id, u.username, u.first_name, a.added_at
                FROM admins a
                JOIN users u ON a.user_id = u.user_id
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # ==================== DOWNLOAD HISTORY ====================

    async def add_download(self, user_id: int, url: str, download_type: str):
        """Добавить запись о скачивании"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO download_history (user_id, url, download_type) VALUES (?, ?, ?)",
                (user_id, url, download_type)
            )
            await db.commit()

    async def get_user_downloads(self, user_id: int) -> List[Dict]:
        """Получить историю скачиваний пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM download_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # ==================== LOGS ====================

    async def add_log(self, user_id: int, action: str, details: str = ""):
        """Добавить лог"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO logs (user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action, details)
            )
            await db.commit()

    async def get_user_logs(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Получить логи пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM logs
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_all_logs(self, limit: int = 100) -> List[Dict]:
        """Получить все логи"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT l.*, u.username, u.first_name
                FROM logs l
                JOIN users u ON l.user_id = u.user_id
                ORDER BY l.timestamp DESC
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def clear_logs(self):
        """Очистить все логи"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM logs")
            await db.commit()

    # ==================== SETTINGS ====================

    async def get_setting(self, key: str) -> Optional[str]:
        """Получить значение настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_setting(self, key: str, value: str):
        """Установить значение настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    async def get_stats(self) -> Dict:
        """Получить статистику бота"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            async with db.execute("""
                SELECT COUNT(*) FROM users
                WHERE last_activity >= datetime('now', '-7 days')
            """) as cursor:
                active_users = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM download_history") as cursor:
                total_downloads = (await cursor.fetchone())[0]

            async with db.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1") as cursor:
                banned_users = (await cursor.fetchone())[0]

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_downloads": total_downloads,
                "banned_users": banned_users
            }

    # ==================== FUNCTION STATS ====================

    async def log_function_use(self, user_id: int, function_name: str):
        """Записать использование функции"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO function_stats (user_id, function_name) VALUES (?, ?)",
                (user_id, function_name)
            )
            await db.commit()

    async def get_function_stats(self) -> Dict:
        """Получить статистику по функциям"""
        async with aiosqlite.connect(self.db_path) as db:
            functions = ['ascii', 'qr', 'downloader', 'video_round']
            stats = {}
            for func in functions:
                async with db.execute(
                    "SELECT COUNT(*) FROM function_stats WHERE function_name = ?", (func,)
                ) as cursor:
                    stats[func] = (await cursor.fetchone())[0]
            return stats

    async def get_user_function_stats(self, user_id: int) -> List[Dict]:
        """Получить статистику функций пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT function_name, COUNT(*) as count
                FROM function_stats
                WHERE user_id = ?
                GROUP BY function_name
                ORDER BY count DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Получить топ пользователей по активности"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT fs.user_id, u.username, u.first_name, COUNT(*) as total_actions
                FROM function_stats fs
                JOIN users u ON fs.user_id = u.user_id
                GROUP BY fs.user_id
                ORDER BY total_actions DESC
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # ==================== TICKETS ====================

    async def create_ticket(self, user_id: int, username: str, first_name: str, message: str) -> int:
        """Создать тикет поддержки"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tickets (user_id, username, first_name, message) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, message)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Получить тикет"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_open_tickets(self) -> List[Dict]:
        """Получить все открытые тикеты"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM tickets WHERE status = 'open' ORDER BY created_at DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def close_ticket(self, ticket_id: int):
        """Закрыть тикет"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tickets SET status = 'closed', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (ticket_id,)
            )
            await db.commit()

    async def get_user_tickets(self, user_id: int) -> List[Dict]:
        """Получить тикеты пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # ==================== SPAM PROTECTION ====================

    async def log_spam_action(self, user_id: int, action: str):
        """Записать спам-действие"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO spam_log (user_id, action) VALUES (?, ?)",
                (user_id, action)
            )
            await db.commit()

    async def get_recent_spam_actions(self, user_id: int, seconds: int = 10) -> int:
        """Получить количество спам-действий за последние N секунд"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM spam_log
                WHERE user_id = ?
                AND timestamp >= datetime('now', ?)
            """, (user_id, f'-{seconds} seconds')) as cursor:
                return (await cursor.fetchone())[0]

    async def clear_old_spam_logs(self, hours: int = 24):
        """Очистить старые спам-логи"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM spam_log WHERE timestamp < datetime('now', ?)",
                (f'-{hours} hours',)
            )
            await db.commit()

    # ==================== DESIGN SETTINGS ====================

    async def get_design_setting(self, key: str) -> Optional[str]:
        """Получить настройку дизайна"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value FROM design_settings WHERE key = ?", (key,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_design_setting(self, key: str, value: str):
        """Установить настройку дизайна"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO design_settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            await db.commit()

    async def get_all_design_settings(self) -> Dict:
        """Получить все настройки дизайна"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM design_settings") as cursor:
                rows = await cursor.fetchall()
                return {row['key']: row['value'] for row in rows}

    # ==================== SERVER MONITORING ====================

    async def add_server_check(self, server_name: str, server_url: str):
        """Добавить сервер для мониторинга"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO server_checks (server_name, server_url) VALUES (?, ?)",
                (server_name, server_url)
            )
            await db.commit()

    async def remove_server_check(self, server_id: int):
        """Удалить сервер из мониторинга"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM server_checks WHERE id = ?", (server_id,))
            await db.commit()

    async def get_all_server_checks(self) -> List[Dict]:
        """Получить все серверы для мониторинга"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM server_checks WHERE is_active = 1") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_server_status(self, server_id: int, status: str):
        """Обновить статус сервера"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE server_checks SET last_status = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?",
                (status, server_id)
            )
            await db.commit()

    async def get_new_users_count_since(self, hours: int = 24) -> int:
        """Получить количество новых пользователей за последние N часов"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', ?)",
                (f'-{hours} hours',)
            ) as cursor:
                return (await cursor.fetchone())[0]

    async def get_weekly_stats(self) -> Dict:
        """Получить статистику за неделю"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT DATE(timestamp) as day, COUNT(*) as count
                FROM function_stats
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY day ORDER BY day
            """) as cursor:
                rows = await cursor.fetchall()
                days = {}
                for row in rows:
                    days[row[0]] = row[1]
                return days

    # ==================== SCHEDULED BROADCASTS ====================

    async def init_scheduled_table(self):
        """Создать таблицу отложенных рассылок"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    message_text TEXT,
                    schedule_time TIMESTAMP,
                    filter_type TEXT DEFAULT 'all',
                    status TEXT DEFAULT 'pending',
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def add_scheduled_message(self, admin_id: int, message_text: str,
                                     schedule_time: str, filter_type: str = 'all'):
        """Добавить отложенную рассылку"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO scheduled_messages
                   (admin_id, message_text, schedule_time, filter_type)
                   VALUES (?, ?, ?, ?)""",
                (admin_id, message_text, schedule_time, filter_type)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_pending_scheduled_messages(self) -> List[Dict]:
        """Получить ожидающие отложенные рассылки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT * FROM scheduled_messages
                   WHERE status = 'pending'
                   AND schedule_time <= datetime('now')
                   ORDER BY schedule_time ASC"""
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def mark_scheduled_sent(self, msg_id: int, sent: int, failed: int):
        """Отметить рассылку как отправленную"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE scheduled_messages
                   SET status = 'sent', sent_count = ?, failed_count = ?
                   WHERE id = ?""",
                (sent, failed, msg_id)
            )
            await db.commit()

    async def get_filtered_users(self, filter_type: str) -> List[Dict]:
        """Получить пользователей по фильтру"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if filter_type == 'all':
                async with db.execute(
                    "SELECT * FROM users ORDER BY joined_at DESC"
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

            elif filter_type == 'active':
                async with db.execute(
                    """SELECT * FROM users
                       WHERE last_activity >= datetime('now', '-7 days')
                       AND is_banned = 0
                       ORDER BY last_activity DESC"""
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

            elif filter_type == 'banned':
                async with db.execute(
                    "SELECT * FROM users WHERE is_banned = 1 ORDER BY joined_at DESC"
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

            elif filter_type == 'admins':
                async with db.execute(
                    """SELECT u.* FROM users u
                       JOIN admins a ON u.user_id = a.user_id
                       ORDER BY u.joined_at DESC"""
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

            return []

    async def search_users(self, query: str) -> List[Dict]:
        """Поиск пользователей по ID, username или имени"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            try:
                user_id = int(query)
                async with db.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return [dict(row)] if row else []
            except ValueError:
                async with db.execute(
                    """SELECT * FROM users
                       WHERE username LIKE ? OR first_name LIKE ?
                       LIMIT 20""",
                    (f'%{query}%', f'%{query}%')
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]


# Singleton instance
db = Database()
