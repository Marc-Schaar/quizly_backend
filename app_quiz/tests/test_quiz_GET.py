from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_utils import (
    create_user1,
    create_user2,
    create_quiz_for_user1,
    create_quiz_for_user2,
)


class TestListAndDetailQuiz(APITestCase):
    def setUp(self):
        (self.user, self.user_client) = create_user1()
        (self.user2, self.user_client2) = create_user2()
        (self.quiz_1, questions1) = create_quiz_for_user1(self.user)
        (self.quiz_2, questions2) = create_quiz_for_user2(self.user2)
        self.question_1 = questions1[0]
        self.question_2 = questions2[0]

    def test_get_quiz_list_200(self):
        url = reverse("quiz_list")
        response = self.user_client.get(url, format="json")
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, list)
        self.assertGreaterEqual(len(response_data), 1)

    def test_get_quiz_list_401(self):
        url = reverse("quiz_list")
        self.user_client.force_authenticate(user=None)
        response = self.user_client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_quiz_detail_200(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        response = self.user_client.get(url, format="json")
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)
        self.assertEqual(response_data["id"], self.quiz_1.id)
        self.assertEqual(response_data["title"], self.quiz_1.title)
        self.assertEqual(response_data["description"], self.quiz_1.description)
        self.assertEqual(len(response_data["questions"]), 1)
        question_titles = [q["question_title"] for q in response_data["questions"]]
        self.assertIn(self.question_1.question_title, question_titles)

    def test_get_quiz_detail_401(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        self.user_client.force_authenticate(user=None)
        response = self.user_client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_quiz_detail_403(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        response = self.user_client2.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_quiz_detail_404(self):
        url = reverse("quiz_detail", kwargs={"id": 9999})
        response = self.user_client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
