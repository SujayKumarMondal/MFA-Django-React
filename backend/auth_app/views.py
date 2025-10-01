from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login, logout
from .serializers import RegisterSerializer, LoginSerializer, MFAVerifySerializer
from .models import User
from .utils import generate_mfa_secret, generate_qr_code_uri, verify_totp, send_otp_email, store_otp, get_otp
import random
import jwt
import os
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

JWT_SECRET = os.getenv("SECRET_KEY")
ACCESS_TOKEN_LIFETIME = int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME", 300))
REFRESH_TOKEN_LIFETIME = int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME", 3600))

def create_jwt(user, token_type="access"):
    lifetime = ACCESS_TOKEN_LIFETIME if token_type=="access" else REFRESH_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(seconds=lifetime),
        "type": token_type
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        return None

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({"message": "User registered"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                if "unique" in str(e).lower() or "already exists" in str(e).lower():
                    return Response({"error": "User already registered"}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Check for duplicate email error in serializer errors
        if "email" in serializer.errors:
            for err in serializer.errors["email"]:
                if "unique" in err.lower() or "already exists" in err.lower():
                    return Response({"error": "User already registered"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access = create_jwt(user, "access")
            refresh = create_jwt(user, "refresh")
            return Response({"access": access, "refresh": refresh})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MFASetupView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.mfa_secret:
            user.mfa_secret = generate_mfa_secret()
            user.mfa_enabled = True
            user.save()
        qr_code = generate_qr_code_uri(user.email, user.mfa_secret)
        return Response({"qr_code": qr_code})

class MFAVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            user = request.user
            # Check TOTP first
            if user.mfa_enabled and verify_totp(user.mfa_secret, token):
                return Response({"message": "MFA verified"})
            # Otherwise check OTP from email
            otp = get_otp(user.email)
            if otp and otp == token:
                return Response({"message": "MFA verified via OTP"})
            return Response({"message": "Invalid MFA token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MFASendOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            email = request.user.email
            if not email:
                return Response({"error": "User email not found."}, status=status.HTTP_400_BAD_REQUEST)
            otp = str(random.randint(100000, 999999))
            store_otp(email, otp)
            send_otp_email(email, otp)
            return Response({"message": "OTP sent to email"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        payload = decode_jwt(refresh_token)
        if payload and payload.get("type")=="refresh":
            user = User.objects.get(id=payload["user_id"])
            access = create_jwt(user, "access")
            return Response({"access": access})
        return Response({"message": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})
