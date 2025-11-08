# backend/auth_app/utils.py
import pyotp
import qrcode
import io
import base64
import redis
import os
from django.core.mail import send_mail
from django.conf import settings

# Redis setup - ensure REDIS_HOST and REDIS_PORT in env
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception:
    r = None

def generate_mfa_secret():
    """
    Generate a base32 secret suitable for TOTP authenticator apps.
    """
    return pyotp.random_base32()

def generate_qr_code_base64(user_email, secret, issuer_name="MFA Auth"):
    """
    Return a data URI (PNG) with QR code of provisioning URI for authenticator apps.
    """
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name=issuer_name)
    # generate QR code image
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{img_b64}"

def verify_totp(secret, token):
    """
    Verify TOTP token. Returns True/False.
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # allow 1-step window
    except Exception:
        return False

def send_otp_email(to_email, otp, subject="Your OTP Code"):
    """
    Send plain OTP email using Django's send_mail. Ensure EMAIL_* settings are configured.
    """
    try:
        send_mail(
            subject,
            f"Your OTP code is: {otp}",
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False

def store_otp(email, otp, expiry=300):
    """
    Store OTP in redis with expiry (seconds). Key: otp:{email}
    """
    if r:
        try:
            r.setex(f"otp:{email}", expiry, otp)
            return True
        except Exception:
            return False
    return False

def get_otp(email):
    if r:
        try:
            return r.get(f"otp:{email}")
        except Exception:
            return None
    return None
