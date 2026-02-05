"""Serializers for quiz and question models.

This module provides three serializers used by the quiz API:
- `QuestionSerializer` - serializes `Question` model fields for read operations.
- `QuizSerializer` - read-only representation of `Quiz` with nested questions.
- `QuizCreateSerializer` - write serializer that accepts a YouTube `url`
  and validates/extracts the `video_id` used to populate `video_url` and
  generate questions.

Docstring style follows the conventions used in `app_auth.api.serializers`:
- Module-level description followed by concise per-class docstrings.
"""

from rest_framework import serializers
import re
import urllib.parse
from app_quiz.models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for the `Question` model.

    Fields serialized:
    - `id`: Database primary key.
    - `question_title`: Short text of the question.
    - `question_options`: JSON list/dict of possible answers.
    - `answer`: The correct answer as stored in the model.
    - `created_at`, `updated_at`: Timestamps managed by Django.

    This serializer is intended for read-only nested usage inside quiz
    representations and does not provide custom validation or write support.
    """

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
    """Read-only serializer for the `Quiz` model.

    Provides a representation suitable for list/detail views. It exposes a
    read-only `url` field (source is populated by the view) and a nested
    `questions` list using `QuestionSerializer`.
    """

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
    """Serializer for creating a `Quiz` from a YouTube link.

    Intended use:
    - Accepts a write-only `url` containing a YouTube link.
    - Validates the link and extracts `video_id` (stored on `self.video_id`).
    - Creation flows (views) can use the `video_id` to fetch/transcribe video
      content and populate `title`, `description`, `video_url`, and generated
      `questions`.

    Fields:
    - `url` (write-only): YouTube URL provided by the client.
    - `questions` (read-only): Nested `QuestionSerializer` populated after
      quiz generation.

    Validation:
    - `validate_url` ensures the submitted URL is a YouTube link and that the
      extracted `video_id` matches expected format. On success, `self.video_id`
      is set for later use by the view. Raises `serializers.ValidationError`
      with a clear message on failure.
    """

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
        """Validate `value` is a YouTube URL and extract `video_id`.

        On success sets `self.video_id` for use by the view that creates the
        quiz. Raises `serializers.ValidationError` with a German message when
        the URL or video id is invalid to match existing project messages.
        """
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
