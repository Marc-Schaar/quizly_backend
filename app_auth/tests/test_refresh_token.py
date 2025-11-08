from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TestRefreshToken(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="your_username",
            password="your_password",
            email="email@mail.de",
        )

        self.user_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.user_client.cookies["access_token"] = access_token
        self.user_client.cookies["refresh_token"] = str(refresh)
        self.user_client.force_authenticate(user=self.user)

    def test_refresh_token_200(self):
        url = reverse("token_refresh")
        response = self.user_client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "detail": "Token refreshed",
                "access": response.data.get("access"),
            },
        )

    def test_refresh_token_401(self):
        url = reverse("token_refresh")
        payload = {}
        self.user_client.force_authenticate(user=None)
        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
