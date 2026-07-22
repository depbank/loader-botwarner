"""
Генерация QR-кодов
"""
import qrcode
from io import BytesIO


async def generate_qr(text: str) -> BytesIO:
    """Генерирует QR-код из текста"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio
