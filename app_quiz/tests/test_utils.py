from django.contrib.auth.models import User
from app_quiz.models import Quiz, Question
from rest_framework.test import APIClient

def create_user1():
    user1 = User.objects.create_user(
        username="user1",
        password="password1",
        email="user1@mail.de",
    )
    client1 = APIClient()
    client1.force_authenticate(user=user1)
    return user1, client1

def create_user2():
    user2 = User.objects.create_user(
        username="user2",
        password="password2",
        email="user2@mail.de",
    )
    client2 = APIClient()
    client2.force_authenticate(user=user2)
    return user2, client2

def create_quiz_for_user1(user1):
    quiz1 = Quiz.objects.create(
        title="Quiz von User1",
        description="Beschreibung User1 Quiz.",
        video_url="http://example.com/video1",
        creator=user1,
    )
    question1 = Question.objects.create(
        quiz=quiz1,
        question_title="Was ist 2 + 2?",
        question_options=["3", "4", "5", "6"],
        answer="4",
    )
    return quiz1, [question1]

def create_quiz_for_user2(user2):
    quiz2 = Quiz.objects.create(
        title="Quiz von User2",
        description="Beschreibung User2 Quiz.",
        video_url="http://example.com/video2",
        creator=user2,
    )
    question2 = Question.objects.create(
        quiz=quiz2,
        question_title="Was ist die Hauptstadt von Frankreich?",
        question_options=["Berlin", "Madrid", "Paris", "Rom"],
        answer="Paris",
    )
    return quiz2, [question2]
