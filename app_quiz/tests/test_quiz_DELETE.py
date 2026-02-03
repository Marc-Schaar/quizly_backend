from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_utils import (
    create_user1,
    create_user2,
    create_quiz_for_user1,
    create_quiz_for_user2,
)


class TestDeleteQuiz(APITestCase):
    def setUp(self):
        (self.user, self.user_client) = create_user1()
        (self.user2, self.user_client2) = create_user2()
        (self.quiz_1, questions1) = create_quiz_for_user1(self.user)
        (self.quiz_2, questions2) = create_quiz_for_user2(self.user2)
        self.question_1 = questions1[0]
        self.question_2 = questions2[0]

    def test_delete_quiz_204(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204)

    def test_delete_quiz_401(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        self.user_client.logout()
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401)

    def test_delete_quiz_403(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        response = self.user_client2.delete(url)
        self.assertEqual(response.status_code, status.HHTP_403)

    def test_delete_quiz_404(self):
        url = reverse("quiz_detail", kwargs={"id": 999999})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HHTP_404)
        
