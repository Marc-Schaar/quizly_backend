from rest_framework import generics
from .serializers import QuizSerializer
from yt_dlp import YoutubeDL
import json
import tempfile
import whisper
from rest_framework.serializers import ValidationError




class CreateQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    def extract_audio_info(self, video_url):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_filename = tmp_file.name

        ydl_opts = {

            "format": "bestaudio/best",

            "outtmpl": tmp_filename,

            "quiet": True,

            "noplaylist": True,

        }

        URL = video_url

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(URL, download=False)

            return(json.dumps(ydl.sanitize_info(info)))

            
    def get_audio_as_text(self, audio_info):
        model = whisper.load_model("turbo")
        result = model.transcribe(audio_info)
        return(result["text"])

        
    def perform_create(self, serializer):
        creator = self.request.user
        video_url = self.request.data.get("url")
        audio_info = self.extract_audio_info(video_url)
        text = self.get_audio_as_text(audio_info)
        print("Audio file extracted: ", audio_info)
        print("Text:", text)

        serializer.save(creator=creator, video_url=video_url)
        




