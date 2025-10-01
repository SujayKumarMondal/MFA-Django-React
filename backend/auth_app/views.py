# backend/auth_app/views.py
import os
import random
import jwt
from datetime import datetime, timedelta

from django.contrib.auth import logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RegisterSerializer, LoginSerializer, MFAVerifySerializer
from .models import User
from .utils import (
    generate_mfa_secret,
    generate_qr_code_uri,
    verify_totp,
    send_otp_email,
    store_otp,
    get_otp,
)
from auth_app.redis_pubsub import publish_event  # our publisher utility

# JWT config
JWT_SECRET = os.getenv("SECRET_KEY")
ACCESS_TOKEN_LIFETIME = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", 300))
REFRESH_TOKEN_LIFETIME = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", 3600))


def create_jwt(user: User, token_type: str = "access") -> str:
    lifetime = ACCESS_TOKEN_LIFETIME if token_type == "access" else REFRESH_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(seconds=lifetime),
        "type": token_type,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # PyJWT >=2 returns str, older versions return bytes — ensure str
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def publish_to_user_event(user_email: str, event_name: str, extra: dict | None = None) -> None:
    """
    Helper to publish an event to the default `auth_events` channel.
    extra: additional safe fields to include (avoid secrets)
    """
    payload = {
        "email": user_email,
        "timestamp": datetime.utcnow().isoformat()
    }
    if extra:
        # ensure extra doesn't contain OTPs or secrets
        payload.update(extra)
    publish_event("auth_events", event_name, payload)


# ---------------------------
# Views
# ---------------------------

class RegisterView(APIView):
    """Register a new user"""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                # publish event (DO NOT include OTP or mfa_secret)
                publish_to_user_event(user.email, "user_registered", {"user_id": user.id})
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                # handle unique constraint or other DB errors gracefully
                if "unique" in str(e).lower() or "already exists" in str(e).lower():
                    return Response({"error": "User already registered"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Inspect serializer errors for duplicate email
        if "email" in serializer.errors:
            for err in serializer.errors["email"]:
                if "unique" in err.lower() or "already exists" in err.lower():
                    return Response({"error": "User already registered"}, status=status.HTTP_400_BAD_REQUEST)
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


class MFASetupView(APIView):
    """Generate MFA secret and QR code for TOTP."""
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # create secret and enable MFA (persist in DB)
        if not user.mfa_secret:
            user.mfa_secret = generate_mfa_secret()
            user.mfa_enabled = True
            user.save()

        # generate QR png data uri (this contains provisioning URI image — do NOT publish the secret)
        qr_code = generate_qr_code_uri(user.email, user.mfa_secret)

        # publish event noting MFA setup occurred (do NOT include secret or QR)
        publish_to_user_event(user.email, "mfa_setup", {"user_id": user.id})

        return Response({"qr_code": qr_code})


class MFAVerifyView(APIView):
    """Verify TOTP (from authenticator app) or OTP (email)."""
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        user = request.user

        # TOTP verification (preferred)
        if user.mfa_enabled and verify_totp(user.mfa_secret, token):
            publish_to_user_event(user.email, "mfa_verified_totp", {"user_id": user.id})
            return Response({"message": "MFA verified via TOTP"})

        # fallback to email OTP (OTP stored in Redis)
        otp = get_otp(user.email)
        if otp and otp == token:
            # don't publish the OTP value
            publish_to_user_event(user.email, "mfa_verified_otp", {"user_id": user.id})
            return Response({"message": "MFA verified via OTP"})

        return Response({"message": "Invalid MFA token"}, status=status.HTTP_400_BAD_REQUEST)


class MFASendOTPView(APIView):
    """Generate OTP, store in Redis, and send via email. Publish event without OTP contents."""
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            email = request.user.email
            if not email:
                return Response({"error": "User email not found."}, status=status.HTTP_400_BAD_REQUEST)

            otp = str(random.randint(100000, 999999))
            store_otp(email, otp)       # Save OTP in Redis (internal)
            send_otp_email(email, otp)  # Send the OTP over email
            # Publish that an OTP was sent — DO NOT include the OTP value
            publish_to_user_event(email, "otp_sent", {"user_id": request.user.id})
            return Response({"message": "Verify OTP from Authenticator App"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
    """Refresh access token using refresh token"""

    def post(self, request):
        refresh_token = request.data.get("refresh")
        payload = decode_jwt(refresh_token)
        if payload and payload.get("type") == "refresh":
            try:
                user = User.objects.get(id=payload["user_id"])
                access = create_jwt(user, "access")
                return Response({"access": access})
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout user and publish an event"""

    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user.email if request.user else None
        logout(request)
        if email:
            publish_to_user_event(email, "user_logged_out")
        return Response({"message": "Logged out successfully"})
