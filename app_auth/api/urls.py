"""Authentication API URL patterns for `app_auth`.

Endpoints provided:
- `register/` - Register a new user.
- `login/` - Obtain JWT tokens and set cookies.
- `logout/` - Clear authentication cookies.
- `token/refresh/` - Refresh access token using cookie-stored refresh token.
"""

from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    CookieTokenRefreshView,
    RegistrationView,
)


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
]
