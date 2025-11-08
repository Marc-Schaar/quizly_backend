from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuizSerializer


class createQuizView(generics.CreateAPIView):
    serializer_class = QuizSerializer
