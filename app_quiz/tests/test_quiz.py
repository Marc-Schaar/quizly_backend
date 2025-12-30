from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from app_quiz.models import Question, Quiz
from unittest.mock import patch, Mock
import json


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
            question_title="What is 2 + 2?",
            question_options=["3", "4", "5", "6"],
            answer="4",
        )
        self.question_2 = Question.objects.create(
            quiz=self.quiz_1,
            question_title="What is the capital of France?",
            question_options=["Berlin", "Madrid", "Paris", "Rome"],
            answer="Paris",
        )

    @patch("app_quiz.api.views.CreateQuizView.generate_quiz_from_text")
    @patch("app_quiz.api.views.CreateQuizView.parse_audio_into_text")
    @patch("app_quiz.api.views.CreateQuizView.download_audio")
    def test_create_quiz_200(self, mock_download, mock_parse_audio, mock_generate):
        mock_download.return_value = "/tmp/test.m4a"
        mock_parse_audio.return_value = "dummy transcript"
        mock_generate.return_value = Mock(
            candidates=[
                Mock(
                    content=Mock(
                        parts=[
                                Mock(
                                    text=json.dumps(
                                        {
                                            "title": "Test Quiz",
                                            "description": "Test description",
                                            "questions": [
                                                {
                                                    "question_title": "Q1",
                                                    "question_options": [
                                                        "A",
                                                        "B",
                                                        "C",
                                                        "D",
                                                    ],
                                                    "answer": "A",
                                                }
                                            ],
                                        }
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        
        url = reverse("create_quiz")
        payload = {"url": "https://www.youtube.com/watch?v=ok-plXXHlWw"}
        response = self.user_client.post(url, payload, format="json")
        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response_data)
        self.assertIn("title", response_data)
        self.assertIn("description", response_data)
        self.assertIn("created_at", response_data)
        self.assertIn("updated_at", response_data)
        self.assertIn("video_url", response_data)
        self.assertIn("questions", response_data)
        self.assertIsInstance(response_data["questions"], list)
        self.assertGreaterEqual(len(response_data["questions"]), 1)
        question = response_data["questions"][0]
        self.assertIn("id", question)
        self.assertIn("question_title", question)
        self.assertIn("question_options", question)
        self.assertIn("answer", question)
        self.assertIn("created_at", question)
        self.assertIn("updated_at", question)
        self.assertIsInstance(question["question_options"], list)
        self.assertEqual(len(question["question_options"]), 4)
