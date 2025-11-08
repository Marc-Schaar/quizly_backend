from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestLogin(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="your_username",
            password="your_password",
            email="email@mail.de",
        )
        self.user_client = APIClient()

    def test_login_user_200(self):
        url = reverse("login")
        payload = {"username": "your_username", "password": "your_password"}
        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "detail": "Login successfully!",
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                    "email": self.user.email,
                },
            },
        )
        self.assertIsInstance(response.json(), dict)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)
        self.assertTrue(response.cookies["refresh_token"].value)

    def test_login_user_401(self):
        url = reverse("login")
        inavlid_payload = [
            {"username": "wrong_username", "password": "wrong_password"},
            {"username": "your_username", "password": "wrong_password"},
            {"username": "wrong_username", "password": "your_password"},
            {"username": "", "password": "your_password"},
            {"username": "wrong_username", "password": ""},
        ]
        for payload in inavlid_payload:
            response = self.user_client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.json(),
                {"error": "Username oder Passwort falsch"},
            )
