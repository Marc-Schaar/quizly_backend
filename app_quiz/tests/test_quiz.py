from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from app_quiz.models import Question, Quiz


class TestQuiz(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="your_username",
            password="your_password",
            email="email@mail.de",
        )

        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

        self.quiz_1 = Quiz.objects.create(
                title="Sample Quiz",
                description="This is a sample quiz description.",
                video_url="http://example.com/video",
        )

        self.question_1 = Question.objects.create(
                quiz=self.quiz_1,
                question_title= "What is 2 + 2?",
                question_options =["3", "4", "5", "6"],
                answer= "4",
            
            
        )
        self.question_2 = Question.objects.create(
                quiz=self.quiz_1,
                question_title= "What is the capital of France?",
                question_options= ["Berlin", "Madrid", "Paris", "Rome"],
                answer= "Paris",
        )

    def test_create_quiz_200(self):

        url = reverse("create_quiz")
        data = {
            "title": "Sample Quiz",
            "description": "This is a sample quiz description.",
            "video_url": "http://example.com/video",
            "questions": [1, 2],
        }
        response = self.user_client.post(url, data, format="json")
        print("Response: ", response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(len(response.data["questions"]), 2)
