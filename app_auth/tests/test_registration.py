from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestRegistration(APITestCase):
    def setUp(self):
        self.user_client = APIClient()

    def test_register_user_200(self):
        url = reverse("registration")
        payload = {
            "username": "user_test",
            "password": "password123",
            "repeated_password": "password123",
            "email": "user@mail.de"
        }

        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User created successfully!")
        self.assertIsInstance(response.json(), dict)

    def test_register_user_400(self):
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
