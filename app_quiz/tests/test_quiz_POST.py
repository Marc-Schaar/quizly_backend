from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock
import json
from .test_utils import create_user1, create_quiz_for_user1


class TestCreateQuiz(APITestCase):
    """Tests for quiz creation endpoint.

    Includes happy-path creation and negative cases where the client is
    unauthenticated. The unauthenticated test clears forced
    authentication with `self.user_client.force_authenticate(user=None)`
    and expects HTTP 401.
    """

    def setUp(self):
        """Create a user and an example quiz used by the tests."""
        self.user, self.user_client = create_user1()
        self.quiz_1, questions = create_quiz_for_user1(self.user)
        self.question_1 = questions[0]

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

    def test_create_quiz_400(self):
        url = reverse("create_quiz")
        payloads = [
            {},
            {"url": None},
            {"url": "   "},
            {"url": "x" * 1000},
            {"url": 12345},
            {"url": ["https://www.youtube.com/watch?v=ok-plXXHlWw"]},
            {"url": {"link": "https://www.youtube.com/watch?v=ok-plXXHlWw"}},
            {"url": "http://youtube.com"},
            {"url": "https://youtu.be/"},
            {"url": "https://www.youtube.com/watch"},
            {"url": "https://www.youtube.com/watch?v=!!!@@@###"},
            {"url": ""},
            {"url": "invalid_url"},
            {"url": "ftp://example.com/video"},
            {"url": "https://www.notyoutube.com/watch?v=ok-plXXHlWw"},
            {"url": "https://www.youtube.com/watch?v="},
            {"url": "https://www.youtube.com/watch?v=invalid_id"},
            {"wrong_field": "https://www.youtube.com/watch?v=ok-plXXHlWw"},
        ]
        for payload in payloads:
            response = self.user_client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_quiz_401(self):
        """Unauthenticated POST requests must be rejected with 401.

        The test removes forced authentication from the client and posts
        a valid payload; the API should respond with HTTP 401.
        """
        url = reverse("create_quiz")
        payload = {"url": "https://www.youtube.com/watch?v=ok-plXXHlWw"}
        self.user_client.force_authenticate(user=None)
        response = self.user_client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
