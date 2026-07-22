"""
Конвертер изображений в ASCII Art
"""
import asyncio
import numpy as np
from PIL import Image
import config


async def image_to_ascii(image_path: str) -> str:
    """Конвертирует изображение в ASCII-символы"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _image_to_ascii_sync, image_path)
    return result


def _image_to_ascii_sync(image_path: str) -> str:
    """Синхронная часть конвертации"""
    img = Image.open(image_path)
    width = config.ASCII_WIDTH
    aspect_ratio = img.height / img.width
    height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, height))
    img = img.convert('L')

    pixels = np.array(img)
    chars = config.ASCII_CHARS
    ascii_str = "\n".join(
        "".join(chars[pixel * (len(chars) - 1) // 255] for pixel in row)
        for row in pixels
    )
    return ascii_str
