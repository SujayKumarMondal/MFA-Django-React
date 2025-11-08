from django.urls import path
from .views import (
    RegisterView, LoginView, MFASetupView, MFAVerifyView,
    MFASendOTPView, TokenRefreshView, LogoutView, RequestPasswordResetView,
    ConfirmPasswordResetView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("mfa/setup/", MFASetupView.as_view()),
    path("mfa/verify/", MFAVerifyView.as_view()),
    path("mfa/send-otp/", MFASendOTPView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("reset-password/request/", RequestPasswordResetView.as_view()),
    path("reset-password/confirm/", ConfirmPasswordResetView.as_view()),
]
