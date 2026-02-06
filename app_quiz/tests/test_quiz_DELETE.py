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
    """Tests for deleting quizzes.

    Verifies successful deletion by the owner, and negative cases where the
    client is unauthenticated (uses `self.user_client.logout()`) or not the
    owner of the resource (403). Also checks 404 for non-existent quizzes.
    """
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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_quiz_401(self):
        """Unauthenticated clients should receive HTTP 401 for delete.

        The test logs out the client (clearing authentication) and attempts
        to delete a quiz; the API must reject the request with 401.
        """
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        self.user_client.logout()
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_quiz_403(self):
        url = reverse("quiz_detail", kwargs={"id": self.quiz_1.id})
        response = self.user_client2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_quiz_404(self):
        url = reverse("quiz_detail", kwargs={"id": 999999})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
