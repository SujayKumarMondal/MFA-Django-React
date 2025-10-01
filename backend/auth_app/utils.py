import pyotp
import qrcode
import io
import base64
import redis
import os
from django.core.mail import send_mail

# Redis setup
r = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)

def generate_mfa_secret():
    return pyotp.random_base32()

def generate_qr_code_uri(user_email, secret):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name="MFA Auth")
    img = qrcode.make(uri)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def verify_totp(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

def send_otp_email(to_email, otp):
    from django.conf import settings
    send_mail(
        "Your OTP Code",
        f"Your OTP code is {otp}",
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False,
        reply_to=[settings.EMAIL_HOST_USER]
    )

def store_otp(email, otp, expiry=300):
    r.setex(f"otp:{email}", expiry, otp)

def get_otp(email):
    return r.get(f"otp:{email}")
