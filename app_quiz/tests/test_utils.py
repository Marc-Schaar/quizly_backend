from django.contrib.auth.models import User
from app_quiz.models import Quiz, Question
from rest_framework.test import APIClient

def create_test_user():
    user = User.objects.create_user(
        username="your_username",
        password="your_password",
        email="email@mail.de",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return user, client

def create_quiz_with_questions(user):
    quiz = Quiz.objects.create(
        title="Sample Quiz",
        description="This is a sample quiz description.",
        video_url="http://example.com/video",
        creator=user,
    )
    question_1 = Question.objects.create(
        quiz=quiz,
        question_title="What is 2 + 2?",
        question_options=["3", "4", "5", "6"],
        answer="4",
    )
    question_2 = Question.objects.create(
        quiz=quiz,
        question_title="What is the capital of France?",
        question_options=["Berlin", "Madrid", "Paris", "Rome"],
        answer="Paris",
    )
    return quiz, [question_1, question_2]
