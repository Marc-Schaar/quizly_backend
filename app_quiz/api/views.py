from rest_framework import generics
from .serializers import QuizSerializer
from yt_dlp import YoutubeDL
import tempfile
import whisper
from google import genai
import json
from django.conf import settings


class CreateQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    def download_audio(self, video_url):
        tempfilee = tempfile.gettempdir() + "/%(id)s.%(ext)s"
        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "outtmpl": tempfilee,
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
            print("Error downloading audio:", e)

    def parse_audio_into_text(self, audio_path):
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]

    def generate_quiz_from_text(self, transcript):
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = (
            "The quiz must follow this exact structure:\n"
            "{\n"
            '  "title": "Create a concise quiz title based on the topic of the transcript.",\n'
            '  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",\n'
            '  "questions": [\n'
            "    {\n"
            '      "question_title": "The question goes here.",\n'
            '      "question_options": ["Option A", "Option B", "Option C", "Option D"],\n'
            '      "answer": "The correct answer from the above options"\n'
            "    },\n"
            "    ... (exactly 10 questions)\n"
            "  ]\n"
            "}\n\n"
            "Requirements:\n"
            "- Each question must have exactly 4 distinct answer options.\n"
            "- Only one correct answer is allowed per question, and it must be present in 'question_options'.\n"
            "- The output must be valid JSON and parsable as-is.\n"
            "- Do not include explanations, comments, or any text outside the JSON.\n\n"
            f"Transcript:\n{transcript}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response
    
    def parse_quiz_response(self, quiz_response):
        candidates = getattr(quiz_response, "candidates", [])
        if not candidates:
            raise ValueError("Keine Kandidaten im Response vorhanden")

        parts = getattr(candidates[0].content, "parts", [])
        if not parts:
            raise ValueError("Keine Teile im Content vorhanden")

        content_text = getattr(parts[0], "text", "")
        if not content_text:
            raise ValueError("Kein Text im ersten Part vorhanden")

        content_text = content_text.replace("```json", "").replace("```", "")
        quiz_dict = json.loads(content_text)
        return quiz_dict

    def perform_create(self, serializer):
        creator = self.request.user
        video_url = self.request.data.get("url")
        audio_path = self.download_audio(video_url)
        text = self.parse_audio_into_text(audio_path)
        quiz_data_response = self.generate_quiz_from_text(text)
        quiz_dict= self.parse_quiz_response(quiz_data_response)

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
