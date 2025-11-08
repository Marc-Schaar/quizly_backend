from django.urls import path
from .views import createQuizView


urlpatterns = [
    path("createQuiz/", createQuizView.asView(), name="create_quiz"),
    # path('quizzes/'),
    # path('quizzes/<int:id>/'),
]
