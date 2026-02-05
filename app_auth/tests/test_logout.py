from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TestLogout(APITestCase):
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

    def test_logout_user_200(self):
        url = reverse("logout")
        payload = {}

        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            },
        )
        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.cookies.get("access_token").value, "")
        self.assertEqual(response.cookies.get("refresh_token").value, "")

    def test_logout_user_401(self):
        url = reverse("logout")
        payload = {}
        self.user_client.force_authenticate(user=None)
        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(), {"detail": "Authentication credentials were not provided."}
        )
        self.assertIsInstance(response.json(), dict)



