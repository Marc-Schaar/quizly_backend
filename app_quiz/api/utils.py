from django.conf import settings


import json
import tempfile
import whisper
from google import genai
from google.genai.errors import ClientError
from yt_dlp import YoutubeDL

from rest_framework import serializers


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


def download_audio(video_url: str) -> str:
    """Download audio for the given YouTube `video_url`.

    Parameters:
    - video_url (str): Full YouTube URL or watch link.

    Returns:
    - str: Path to the downloaded audio file (m4a).

    Raises:
    - `serializers.ValidationError` if the download or extraction fails.
    """
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


def parse_audio_into_text(audio_path: str) -> str:
    """Transcribe audio at `audio_path` to plain text using Whisper.

    Parameters:
    - audio_path (str): Filesystem path to the audio file.

    Returns:
    - str: Transcribed text.
    """
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, fp16=False)
    return result["text"]


def generate_quiz_from_text(transcript: str) -> dict:
    """Call Google Gemini to generate a quiz JSON from `transcript`.

    Parameters:
    - transcript (str): The transcribed text to include in the prompt.

    Returns:
    - dict/object: Raw response returned by the GenAI client.

    Raises:
    - `serializers.ValidationError` for API errors; quota (429) is handled
      with a clear error message.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = QUIZ_PROMPT_TEMPLATE.format(transcript=transcript)
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


def parse_quiz_response(quiz_response: dict) -> dict:
    """Extract and parse the JSON quiz payload from the GenAI response.

    Parameters:
    - quiz_response: Raw response returned by `generate_quiz_from_text`.

    Returns:
    - dict: Parsed quiz dictionary with keys `title`, `description`,
      and `questions`.

    Raises:
    - ValueError if the response is empty or cannot be parsed as JSON.
    """
    if not quiz_response.candidates:
        raise ValueError("AI Response is empty")
    try:
        content_text = quiz_response.candidates[0].content.parts[0].text
        content_text = content_text.replace("```json", "").replace("```", "").strip()
        quiz_dict = json.loads(content_text)
        return quiz_dict
    except (IndexError, AttributeError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid response structure: {e}")


def create_quiz_questions(quiz_instance, quiz_dict):
    """Persist questions from `quiz_dict` onto the given `quiz_instance`.

    Parameters:
    - quiz_instance: Saved `Quiz` model instance.
    - quiz_dict (dict): Parsed quiz dictionary containing `questions`.

    Notes:
    - Expects each question dict to include `question_title`,
      `question_options` (list of 4), and `answer`.
    """
    for q in quiz_dict["questions"]:
        quiz_instance.questions.create(
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"],
        )
