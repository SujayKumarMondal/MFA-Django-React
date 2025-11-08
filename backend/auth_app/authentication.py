# backend/auth_app/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
import jwt
from .models import User
import os

JWT_SECRET = os.getenv("SECRET_KEY", getattr(settings, "SECRET_KEY", "change-me"))

class CustomJWTAuthentication(BaseAuthentication):
    """
    Authenticate using Authorization: Bearer <access_token>
    Tokens are verified using our custom jwt.encode scheme.
    """
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith(f"{self.keyword} "):
            return None  # No credentials; DRF moves to next auth class

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Access token expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid access token")

        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Invalid token type")

        try:
            user = User.objects.get(id=payload["user_id"], email=payload["email"])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")

        return (user, None)
