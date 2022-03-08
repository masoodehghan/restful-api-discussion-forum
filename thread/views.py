from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuestionSerializer
from .models import Question
from rest_framework import permissions, status
from django.utils.text import slugify
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse



   

class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, **args):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True, context={'request':request})
        
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
        
class QuestionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, slug, **args):
        qusetion = Question.objects.get(slug=slug)
        serializer = QuestionSerializer(qusetion, many=False)
        
        return Response({
        'data': serializer.data,
        
    })
    
