import qrcode
import base64
from io import BytesIO
from app.core.security import decode_token

def generate_qr_base64(token: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color=chr(98)+chr(108)+chr(97)+chr(99)+chr(107), back_color=chr(119)+chr(104)+chr(105)+chr(116)+chr(101))
    buffer = BytesIO()
    img.save(buffer, format=chr(80)+chr(78)+chr(71))
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode(chr(117)+chr(116)+chr(102)+chr(45)+chr(56))

def validate_qr_token(token: str):
    return decode_token(token)
