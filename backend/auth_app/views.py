import os, uuid
import jwt
import random
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .authentication import CustomJWTAuthentication
from .serializers import (
    RegisterSerializer, LoginSerializer, MFAVerifySerializer,
    RequestPasswordResetSerializer, ConfirmPasswordResetSerializer,
)
from .models import User
from .utils import (
    generate_mfa_secret, generate_qr_code_base64, verify_totp,
    send_otp_email
)

# ---------------------------
# JWT CONFIG
# ---------------------------
JWT_SECRET = os.getenv("JWT_SECRET", getattr(settings, "SECRET_KEY", "change-me"))
ACCESS_TOKEN_LIFETIME = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", 300))      # 5 min
REFRESH_TOKEN_LIFETIME = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", 3600))   # 1 hr


def create_jwt(user: User, token_type: str = "access") -> str:
    """Create access or refresh token."""
    lifetime = ACCESS_TOKEN_LIFETIME if token_type == "access" else REFRESH_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "type": token_type,
        "exp": datetime.utcnow() + timedelta(seconds=lifetime),
        "iat": datetime.utcnow(),
    }
    if token_type == "refresh":
        payload["jti"] = str(uuid.uuid4())  # Add a unique identifier for the refresh token
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token if isinstance(token, str) else token.decode("utf-8")


def decode_jwt(token: str):
    """Decode JWT and handle expiry/invalid errors."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "expired"}
    except Exception:
        return None


def publish_to_user_event(*_, **__):
    """Optional event/logging hook."""
    return None


# ==============================================================
#                        AUTH VIEWS
# ==============================================================

class RegisterView(APIView):
    """Register a new user"""
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                # Optionally send a welcome or verification email
                return Response(
                    {"message": "User registered successfully", "email": user.email},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Authenticate user and return JWT access & refresh tokens"""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            access = create_jwt(user, "access")
            refresh = create_jwt(user, "refresh")
            publish_to_user_event(user.email, "user_logged_in", {"user_id": user.id})
            return Response({"access": access, "refresh": refresh})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """Accept a refresh token and return a new access token."""
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        decoded = decode_jwt(refresh)
        if not decoded:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        if decoded.get("error") == "expired":
            return Response({"error": "Refresh token expired"}, status=status.HTTP_401_UNAUTHORIZED)
        if decoded.get("type") != "refresh":
            return Response({"error": "Not a refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=decoded.get("user_id"))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        new_access = create_jwt(user, "access")
        return Response({"access": new_access})


class LogoutView(APIView):
    """Stateless logout (frontend clears tokens)."""
    def post(self, request):
        try:
            logout(request)
        except Exception:
            pass
        return Response({"message": "Logged out successfully"})


# ==============================================================
#                        MFA VIEWS
# ==============================================================

class MFASetupView(APIView):
    """Generate MFA secret and QR code for TOTP. Requires authenticated user."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.mfa_secret:
            user.mfa_secret = generate_mfa_secret()
            user.save()

        qr_data_uri = generate_qr_code_base64(user.email, user.mfa_secret, issuer_name="MFA Auth")
        return Response({"mfa_secret": user.mfa_secret, "qr": qr_data_uri})


class MFAVerifyView(APIView):
    """Verify TOTP token from authenticator app."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        user = request.user

        if not user.mfa_secret:
            return Response({"error": "MFA secret not set for user"}, status=status.HTTP_400_BAD_REQUEST)

        if verify_totp(user.mfa_secret, token):
            user.mfa_enabled = True
            user.save()
            publish_to_user_event(user.email, "mfa_enabled", {"user_id": user.id})
            return Response({"message": "MFA verified successfully"})
        return Response({"error": "Invalid or expired TOTP"}, status=status.HTTP_400_BAD_REQUEST)


class MFASendOTPView(APIView):
    """Send a one-time password (OTP) to user's email."""
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user or not user.email:
            return Response({"error": "User email required"}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{random.randint(100000, 999999)}"
        ok = send_otp_email(user.email, otp)

        if ok:
            # store_otp(user.email, otp, expiry=300)
            return Response({"message": "OTP sent to email"})
        return Response({"error": "Failed to send OTP email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================
#                    PASSWORD RESET FLOW
# ==============================================================

class RequestPasswordResetView(APIView):
    """Send password reset link to user's email."""
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Silent success for security
            return Response({"message": "If that account exists, a reset link was sent."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"

        try:
            send_mail(
                "Password reset request",
                f"Click the link to reset your password: {reset_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            publish_to_user_event(user.email, "password_reset_requested", {"user_id": user.id})
            return Response({"message": "If that account exists, a reset link was sent."})
        except Exception as e:
            return Response({"error": "Failed to send reset email", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmPasswordResetView(APIView):
    """Confirm password reset: verify uid+token and update password."""
    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uidb64 = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.set_password(password)
            user.save()
            publish_to_user_event(user.email, "password_reset", {"user_id": user.id})
            return Response({"message": "Password has been reset successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
