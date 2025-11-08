# backend/auth_app/utils.py
import pyotp
import qrcode
import io
import base64
from django.core.mail import send_mail
from django.conf import settings

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

