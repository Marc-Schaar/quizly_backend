from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestLogin(APITestCase):
    """This test class covers two scenarios:
    - Successful login with valid credentials (HTTP 200).
    - Failed login attempts with various invalid credentials (HTTP 401).

    Each test uses `self.user_client` to POST JSON payloads to the
    endpoint resolved by `reverse("login")` and asserts on status codes,
    response body structure, and authentication cookies.
    """

    def setUp(self):
        """Create a test user and initialize the API client.

        The created user has credentials that are used by
        `test_login_user_200` to exercise the happy-path login flow.
        """
        self.user = User.objects.create_user(
            username="your_username",
            password="your_password",
            email="email@mail.de",
        )
        self.user_client = APIClient()

    def test_login_user_200(self):
        """Happy-path: POST valid credentials and expect HTTP 200.

        Asserts that the response JSON contains a success `detail`
        and `user` object matching the created user. Also verifies that
        `access_token` and `refresh_token` cookies are present and
        non-empty on the response.
        """
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
        """Negative tests: various invalid credentials should return 401.

        Iterates over different malformed/incorrect payloads and asserts
        that the API responds with HTTP 401 and the expected localized
        error message.
        """
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
