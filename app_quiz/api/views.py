from django.conf import settings
from django.db import transaction
from rest_framework import generics, serializers
from google import genai
import json
import tempfile
import whisper
from yt_dlp import YoutubeDL
from .serializers import QuizSerializer


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

    def download_audio(self, video_url):
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
            raise serializers.ValidationError(
                {"video_url": f"Audio download failed: {e}"}
            )

    def parse_audio_into_text(self, audio_path):
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]

    def generate_quiz_from_text(self, transcript):
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = self.QUIZ_PROMPT_TEMPLATE.format(transcript=transcript)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response

    def parse_quiz_response(self, quiz_response):
        try:
            content_text = quiz_response.candidates[0].content.parts[0].text
            content_text = content_text.replace("```json", "").replace("```", "").strip()
            quiz_dict = json.loads(content_text)
            return quiz_dict
        except (IndexError, AttributeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid response structure: {e}")

    def perform_create(self, serializer):
        creator = self.request.user
        video_url = self.request.data.get("url")

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
            for q in quiz_dict["questions"]:
                quiz_instance.questions.create(
                    question_title=q["question_title"],
                    question_options=q["question_options"],
                    answer=q["answer"],
                )
