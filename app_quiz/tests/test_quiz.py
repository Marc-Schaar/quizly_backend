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
                creator=self.user,
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
        payload = {
            "title":"Test",
            "description":"Test",
            "url": "https://www.youtube.com/watch?v=ok-plXXHlWw"
        }
        response = self.user_client.post(url, payload, format="json")
        response_data = response.json()
        print("Response: ", response_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("video_url", response.data)
