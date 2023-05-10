from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    profile,
    RegisterUserView,
    UpdatePasswordView,
    UserUpdateView,
    ResetPasswordView,
    ResetPasswordConfirmView,
)


app_name = "accounts"

urlpatterns = [
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        ResetPasswordConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("user-update/<int:pk>/", UserUpdateView.as_view(), name="user_update"),
    path("update-password/", UpdatePasswordView.as_view(), name="update_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", profile, name="profile"),
]
