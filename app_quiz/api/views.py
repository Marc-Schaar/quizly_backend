from rest_framework import generics
from .serializers import QuizSerializer
from yt_dlp import YoutubeDL
import tempfile
import whisper
from google import genai
import json





class CreateQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    def download_audio(self, video_url):
        

        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': tempfile.gettempdir() + '/%(id)s.%(ext)s',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
               
            # with YoutubeDL(ydl_opts) as ydl:
            #     error_code = ydl.download(URLS)
                #print("Error Code:",error_code)
        except Exception as e:
            print("Error downloading audio:", e)


    def parse_audio_into_text(self, audio_info):
        model = whisper.load_model("turbo")
        result = model.transcribe(audio_info)
        return(result["text"])

    def generate_quiz_from_text(self, transcript):
        client = genai.Client()

        prompt = (
            "The quiz must follow this exact structure:\n"
            "{\n"
            '  "title": "Create a concise quiz title based on the topic of the transcript.",\n'
            '  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",\n'
            '  "questions": [\n'
            '    {\n'
            '      "question_title": "The question goes here.",\n'
            '      "question_options": ["Option A", "Option B", "Option C", "Option D"],\n'
            '      "answer": "The correct answer from the above options"\n'
            '    },\n'
            '    ... (exactly 10 questions)\n'
            '  ]\n'
            "}\n\n"
            "Requirements:\n"
            "- Each question must have exactly 4 distinct answer options.\n"
            "- Only one correct answer is allowed per question, and it must be present in 'question_options'.\n"
            "- The output must be valid JSON and parsable as-is.\n"
            "- Do not include explanations, comments, or any text outside the JSON.\n\n"
            f"Transcript:\n{transcript}"
        )

        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response

    def perform_create(self, serializer):
        creator = self.request.user
        video_url = self.request.data.get("url")
        video = self.download_audio(video_url)
        # text = self.parse_audio_into_text(video)
        # print("Text:", text)
        # quiz_data = self.generate_quiz_from_text(text)
        # print("Quiz Data:", quiz_data)
        serializer.save(creator=creator, video_url=video_url)
    
