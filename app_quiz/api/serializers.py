from rest_framework import serializers
import re
import urllib.parse
from app_quiz.models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]


class QuizSerializer(serializers.ModelSerializer):
    url = serializers.URLField(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "url",
            "video_url",
            "questions",
        ]
        read_only_fields = [
            "questions",
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    url = serializers.URLField(write_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "url",
            "video_url",
            "questions",
        ]
        read_only_fields = [
            "title",
            "description",
            "questions",
            "video_url",
        ]

    def validate_url(self, value):
        parsed = urllib.parse.urlparse(value)
        domain = parsed.netloc.lower()

        if domain == "youtu.be":
            video_id = parsed.path.lstrip("/")
        elif domain in ("www.youtube.com", "youtube.com"):
            query = urllib.parse.parse_qs(parsed.query)
            video_id = query.get("v", [None])[0]
        else:
            raise serializers.ValidationError("Ungültige YouTube-URL.")

        if not video_id or not re.match(r"^[\w-]{11}$", video_id):
            raise serializers.ValidationError("Ungültige YouTube-Video-ID.")

        self.video_id = video_id
        return value
