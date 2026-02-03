from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_utils import (
    create_user1,
    create_user2,
    create_quiz_for_user1,
    create_quiz_for_user2,
)


class TestUpdateQuiz(APITestCase):
    def setUp(self):
        (self.user, self.user_client) = create_user1()
        (self.user2, self.user_client2) = create_user2()
        (self.quiz_1, questions1) = create_quiz_for_user1(self.user)
        (self.quiz_2, questions2) = create_quiz_for_user2(self.user2)
        self.question_1 = questions1[0]
        self.question_2 = questions2[0]

    def test_update_quiz_200(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        payload = {
            "title": "Partially Updated Title",
            "description": "Quiz Description",
            "video_url": "https://www.youtube.com/watch?v=example",
        }
        response = self.user_client.patch(url, payload, format="json")
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_data, dict)
        self.assertIsInstance(response_data["questions"], list)
        self.assertIsInstance(question["question_options"], list)

        for field in [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]:
            self.assertIn(field, response_data)

        self.assertGreaterEqual(len(response_data["questions"]), 1)
        question = response_data["questions"][0]
        for field in ["id", "question_title", "question_options", "answer"]:
            self.assertIn(field, question)

        self.assertGreaterEqual(len(question["question_options"]), 1)
        self.assertEqual(response_data["title"], payload["title"])
        self.assertEqual(response_data["description"], payload["description"])
        self.assertEqual(response_data["video_url"], payload["video_url"])

    def test_update_quiz_400(self):
        pass

    def test_update_quiz_401(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        payload = {
            "title": "Partially Updated Title",
            "description": "Quiz Description",
            "video_url": "https://www.youtube.com/watch?v=example",
        }
        self.user_client.logout()
        response = self.user_client2.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_quiz_403(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        payload = {
            "title": "Partially Updated Title",
            "description": "Quiz Description",
            "video_url": "https://www.youtube.com/watch?v=example",
        }
        response = self.user_client2.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_quiz_404(self):
        url = reverse("quiz_detail", kwargs={"id": 99999})
        payload = {
            "title": "Partially Updated Title",
            "description": "Quiz Description",
            "video_url": "https://www.youtube.com/watch?v=example",
        }
        response = self.user_client2.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
   
    