from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestRegistration(APITestCase):
    """Tests for the user registration endpoint.

    Covers successful user creation and a variety of invalid payloads
    that should result in HTTP 400. Uses a plain `APIClient` without
    authentication to simulate new user registration requests.
    """
    def setUp(self):
        self.user_client = APIClient()

    def test_register_user_200(self):
        """Happy-path: valid registration creates a new user (HTTP 201).

        Posts a valid payload and verifies the creation message and that
        the user now exists in the database.
        """
        url = reverse("registration")
        payload = {
            "username": "user_test",
            "password": "password123",
            "repeated_password": "password123",
            "email": "user@mail.de",
        }

        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User created successfully!")
        self.assertIsInstance(response.json(), dict)
        self.assertTrue(get_user_model().objects.filter(username="user_test").exists())

    def test_register_user_400(self):
        """Invalid registration payloads should return HTTP 400.

        Iterates a set of malformed or invalid payloads and asserts the
        API responds with 400 Bad Request and a JSON error body.
        """
        url = reverse("registration")
        invalid_payload = [
            {
                "username": "",
                "password": "password123",
                "repeated_password": "password123",
                "email": "user@mail.de",
            },
            {
                "username": "user_test",
                "password": "",
                "repeated_password": "",
                "email": "user@mail.de",
            },
            {
                "username": "user_test",
                "password": "password123",
                "repeated_password": "password1123",
                "email": "user@mail.de",
            },
            {
                "username": "user_test",
                "password": 2,
                "repeated_password": 2,
                "email": "user@mail.de",
            },
            {
                "username": "user_test",
                "password": "password123",
                "repeated_password": "password123",
                "email": "@mail.de",
            },
            {
                "username": "user_test",
                "password": "password123",
                "repeated_password": "password123",
                "email": "user@",
            },
            {
                "username": "user_test",
                "password": "password123",
                "repeated_password": "password123",
                "email": "",
            },
        ]
        for payload in invalid_payload:
            with self.subTest(payload=payload):
                response = self.user_client.post(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIsInstance(response.json(), dict)
