"""URL patterns for the `app_quiz` API.

Provides endpoints to create a quiz from a YouTube URL, list quizzes,
and retrieve/update/delete a single quiz by ID.
"""

from django.urls import path
from .views import CreateQuizView, QuizListView, QuizDetailView


urlpatterns = [
    path("createQuiz/", CreateQuizView.as_view(), name="create_quiz"),
    path("quizzes/", QuizListView.as_view(), name="quiz_list"),
    path("quizzes/<int:id>/", QuizDetailView.as_view(), name="quiz_detail"),
]
