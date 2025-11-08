from rest_framework import serializers
from app_quiz.models import Quiz, Question


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(
        queryset=Quiz.objects.all(), write_only=True
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "quiz",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
