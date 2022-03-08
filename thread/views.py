from urllib import response
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import QuestionSerializer
from .models import Question
from rest_framework import permissions, status
from django.utils.text import slugify
from .permissions import IsOwnerOrReadOnly


   

class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]
    
    
    def get(self, request, **args):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True, context={'request':request})
        
        return Response(serializer.data)
    
class QuestionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, **args):
        serializer = QuestionSerializer(data=request.data, context={'request':request})
        
        if serializer.is_valid():
            serializer.save(owner=request.user, slug=slugify(serializer.validated_data['title']))
            return Response({'message':'question created.',
                             'data':serializer.data}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


        
class QuestionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_object(self, slug):
        try:
            return Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            return Response({'message':'object is not existed!'}, status=status.HTTP_404_NOT_FOUND)
        
    
    def get(self, request, slug, **args):
        qusetion = self.get_object(slug=slug)
        serializer = QuestionSerializer(qusetion, many=False)
        
        return Response({
        'data': serializer.data,
    })
    
    def put(self, request, slug, **args):
        question = self.get_object(slug)
        self.check_object_permissions(request, question)
        
        serializer = QuestionSerializer(question, data=request.data, many=False)
        if serializer.is_valid(raise_exception=True):
            serializer.save(slug=slugify(serializer.validated_data['title']))
            return Response(serializer.data, status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, **args):
        question = self.get_object(slug)
        self.check_object_permissions(request, question)
        question.delete()
        return Response({'message':'question deleted!'}, status.HTTP_204_NO_CONTENT)