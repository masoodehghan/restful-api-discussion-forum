from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuestionSerializer
from .models import Question
from rest_framework import permissions, status
from django.utils.text import slugify


class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, **args):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        
        return Response(serializer.data)
    
class QuestionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, **args):
        serializer = QuestionSerializer(data=request.data)
        
        if serializer.is_valid():
        
            serializer.save(owner=request.user, slug=slugify(serializer.validated_data['title']))
            return Response({'message':'question created.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
