from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistrationSerializer
from django.contrib.auth.models import User
from django.conf import settings

class RegistrationView(APIView):
    """API endpoint to register a new user.

    Accepts POST requests with `username`, `email`, `password`, and
    `confirmed_password`. Performs basic uniqueness checks for username and
    email, delegates detailed validation to `RegistrationSerializer`, and
    returns HTTP 201 on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        username = request.data.get("username")
        email = request.data.get("email")

        if User.objects.filter(username=username).exists():
            return Response(
                {"username": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"email": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Login endpoint that issues JWT tokens and sets them as cookies.

    Expects `username` and `password` in the POST body. On success, sets
    `access_token` and `refresh_token` cookies and returns basic user info.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)


        try:    
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"error": "Username oder Passwort falsch"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(username=request.data.get("username"), password=request.data.get("password"))

        if not user:
            return Response(
                {"error": "Username oder Passwort falsch"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = super().post(request, *args, **kwargs)


        access_token = serializer.validated_data.get("access")
        refresh_token = serializer.validated_data.get("refresh")


        cookie_settings = {
            "httponly": True,
            "secure": not settings.DEBUG,
            "samesite": "Lax" if settings.DEBUG else "None",
        }

        response.set_cookie(key="access_token", value=access_token, **cookie_settings)
        response.set_cookie(key="refresh_token", value=refresh_token, **cookie_settings)

        response.data = {
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }

        return response


class LogoutView(APIView):
    """Log out the current user by deleting authentication cookies.

    Returns HTTP 200 and clears `access_token` and `refresh_token` cookies.
    """

    def post(self, request):
        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh the access token using the refresh token stored in cookies.

    Reads the `refresh_token` cookie, validates it via the serializer, and
    returns a new `access` token. On success, sets a new `access_token` cookie.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"error": "Refresh token not found in cookies"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get("access")

        response = Response(
            {"detail": "Token refreshed", "access": access_token},
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG, 
            samesite="Lax" if settings.DEBUG else "None",)
        
        return response


