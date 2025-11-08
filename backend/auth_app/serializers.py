# backend/auth_app/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate_email(self, value):
        # Require a Google/Gmail email if that is your rule (adjust as needed)
        value_lower = value.lower()
        if not (value_lower.endswith("@gmail.com") or value_lower.endswith("@googlemail.com")):
            raise serializers.ValidationError("Registration requires a Google/Gmail email address.")
        return value_lower

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        user = User.objects.create_user(email=email, password=password, **validated_data)
        # By default mfa_enabled = False, mfa_secret empty (as in your model)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        password = attrs.get("password")
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError(_("Unable to log in with provided credentials."))
            if not user.is_active:
                raise serializers.ValidationError(_("User account is disabled."))
            attrs["user"] = user
            return attrs
        raise serializers.ValidationError(_("Must include 'email' and 'password'."))


class MFAVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value.isdigit() or len(value) < 4:
            raise serializers.ValidationError("Invalid MFA token format.")
        return value


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("Passwords do not match")
        if len(attrs.get("password", "")) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return attrs
