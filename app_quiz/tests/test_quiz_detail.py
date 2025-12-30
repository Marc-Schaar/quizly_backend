from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from .test_utils import create_test_user, create_quiz_with_questions

class TestDetailQuiz(APITestCase):
    def setUp(self):
        self.user, self.user_client = create_test_user()
        self.quiz_1, questions = create_quiz_with_questions(self.user)
        self.question_1, self.question_2 = questions
