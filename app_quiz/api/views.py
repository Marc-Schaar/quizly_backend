from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from app_quiz.models import Quiz
from .serializers import QuizCreateSerializer, QuizSerializer
from .permissions import IsOwner

from . import utils


class CreateQuizView(generics.CreateAPIView):
    """Create a `Quiz` from a YouTube video.

    Workflow:
    1. Download audio from a YouTube URL.
    2. Transcribe audio to text using Whisper.
    3. Send transcript to Google Gemini (GenAI) to generate a quiz JSON.
    4. Parse the AI response and create `Quiz` and question objects.

    The view uses `QuizCreateSerializer` for input validation and calls
    `perform_create` to orchestrate the end-to-end process.
    """

    serializer_class = QuizCreateSerializer

    def perform_create(self, serializer):
        """Override to orchestrate quiz creation from validated input.

        Steps:
        - Validate serializer and extract `url`/`video_id`.
        - Download audio and transcribe to text.
        - Generate quiz JSON via Gemini and parse it.
        - Save `Quiz` instance and create question records inside a DB
          transaction (atomic).

        Parameters:
        - serializer: An instance of `QuizCreateSerializer` (must be valid).

        Raises:
        - Propagates `serializers.ValidationError` and `ValueError` from
          called methods; transaction ensures rollback on failure.
        """
        creator = self.request.user
        video_url = serializer.validated_data.pop("url")
        video_id = serializer.video_id
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                audio_path = utils.download_audio(video_url)
                text = utils.parse_audio_into_text(audio_path)
                quiz_data_response = utils.generate_quiz_from_text(text)
                quiz_dict = utils.parse_quiz_response(quiz_data_response)


                quiz_instance = serializer.save(
                    creator=creator,
                    video_url=video_url,
                    title=quiz_dict["title"],
                    description=quiz_dict["description"],
                )
                utils.create_quiz_questions(quiz_instance, quiz_dict)


class QuizListView(generics.ListAPIView):
    """List endpoint returning all `Quiz` objects.

    Uses `QuizSerializer` to serialize quiz instances.
    """

    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single `Quiz` by `id`.

    Permissions:
    - Requires authentication and the `IsOwner` permission to modify/delete.
    """

    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    lookup_field = "id"
    permission_classes = [IsAuthenticated, IsOwner]
