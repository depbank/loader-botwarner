"""
Фикс кодировки для Windows
Чтобы русский текст не превращался в '????'
"""
import sys
import io
import locale

def fix_encoding():
    """Принудительно устанавливаем UTF-8 для stdout/stderr"""
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

fix_encoding()
