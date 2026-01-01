from django.conf import settings
from django.db import transaction
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from google import genai
from google.genai.errors import ClientError
import json
import tempfile
import whisper
from yt_dlp import YoutubeDL

from app_quiz.models import Quiz
from .serializers import QuizSerializer
from app_quiz.api.permissions import IsOwner



class CreateQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    QUIZ_PROMPT_TEMPLATE = """
    Generate a JSON object with this exact structure:
    {{
    "title": "...",
    "description": "...",
    "questions": [
        {{
        "question_title": "...",
        "question_options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "..."
        }}
        ... (exactly 10 questions)
    ]
    }}

    Requirements:
    - Only valid JSON, parsable as-is.
    - Do not include ```json, ```, explanations, comments, or any text outside the JSON.
    - Each question must have exactly 4 distinct answer options.
    - Only one correct answer per question, which must exist in 'question_options'.

    Transcript:
    {transcript}
    """

    def download_audio(self, video_url: str) -> str:
        temp_file = tempfile.gettempdir() + "/%(id)s.%(ext)s"
        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "outtmpl": temp_file,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                audio_path = info["requested_downloads"][0]["filepath"]
                return audio_path
        except Exception as e:
            raise serializers.ValidationError({"error": f"Audio download failed: {e}"})

    def parse_audio_into_text(self, audio_path: str) -> str:
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]

    def generate_quiz_from_text(self, transcript: str) -> dict:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = self.QUIZ_PROMPT_TEMPLATE.format(transcript=transcript)
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response
        except ClientError as e:
            if e.response.status_code == 429:
                raise serializers.ValidationError(
                    {"error": "Quota exceeded for Gemini API. Please try again later."}
                )
            raise serializers.ValidationError({"error": f"Error generating quiz: {e}"})

    def parse_quiz_response(self, quiz_response: dict) -> dict:
        if not quiz_response.candidates:
            raise ValueError("AI Response is empty")
        try:
            content_text = quiz_response.candidates[0].content.parts[0].text
            content_text = (
                content_text.replace("```json", "").replace("```", "").strip()
            )
            quiz_dict = json.loads(content_text)
            return quiz_dict
        except (IndexError, AttributeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid response structure: {e}")

    def create_quiz_questions(self, quiz_instance, quiz_dict):
        for q in quiz_dict["questions"]:
            quiz_instance.questions.create(
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"],
            )

    def perform_create(self, serializer):
        creator = self.request.user
        video_url = serializer.validated_data.pop("url")
        video_id = serializer.video_id
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                audio_path = self.download_audio(video_url)
                text = self.parse_audio_into_text(audio_path)
                quiz_data_response = self.generate_quiz_from_text(text)
                quiz_dict = self.parse_quiz_response(quiz_data_response)

                quiz_instance = serializer.save(
                    creator=creator,
                    video_url=video_url,
                    title=quiz_dict["title"],
                    description=quiz_dict["description"],
                )
                self.create_quiz_questions(quiz_instance, quiz_dict)

class QuizListView(generics.ListAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    
class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsOwner]