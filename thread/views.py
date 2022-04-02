from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AnswerSerializer, QuestionSerializer, TagSerializer
from .models import Answer, Question, Tag
from rest_framework import permissions, status
from .permissions import IsOwnerOrReadOnly, CustomIsAdminUser
from django.db.models import Q

   

class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]
    
    
    def get(self, request, **args):
        
        q = ''   # q is serach query

        if request.GET.get('q'):
            q = request.GET.get('q')
        
        tags = Tag.objects.filter(name__icontains=q)
        
        question = Question.objects.distinct().filter(
                                            Q(title__icontains=q) | 
                                            Q(tags__name__icontains=q) | 
                                            Q(owner__first_name__icontains=q) | 
                                            Q(owner__email__icontains=q)
                                            )
        
        
        serializer = QuestionSerializer(question, many=True)
        
        return Response(serializer.data)
    
class QuestionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, **args):
        serializer = QuestionSerializer(data=request.data, context={'request':request})
        
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response({'message':'question created.',
                             'data':serializer.data}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


        
class QuestionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, 
                          IsOwnerOrReadOnly]
    
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
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, **args):
        question = self.get_object(slug)
        self.check_object_permissions(request, question)
        question.delete()
        return Response({'message':'question deleted!'}, status.HTTP_204_NO_CONTENT)
    

class AnswerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated,
                          IsOwnerOrReadOnly]
    
    

    def post(self, request, slug, **args):
        question = Question.objects.get(slug=slug)
        owner = request.user
        
        
        serializer = AnswerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(question=question, owner=owner)
            
            return Response({
                'data':serializer.data,
                'message':'answer created!'
                }, status.HTTP_201_CREATED)
            
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        
    def delete(self, request, pk, **kwargs):
        answer = Answer.objects.get(id=pk)
        self.check_object_permissions(request, answer)
        answer.delete()
        
        return Response({'message':'answer deleted.'}, status.HTTP_204_NO_CONTENT)
    
    
    def put(self, request, pk, **args):
        answer = Answer.objects.get(id=pk)
        self.check_object_permissions(request, answer)
        serializer = AnswerSerializer(answer, request.data, many=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'data':serializer.data,
                             'message':'answer updated.'}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        

class TagView(APIView):
    permission_classes =  [permissions.IsAuthenticatedOrReadOnly,
                           CustomIsAdminUser]
                          
    
    def post(self, request, **args):
        
        self.check_permissions(request=request)
        serializer = TagSerializer(data=request.data, many=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Tag created.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, slug, **args):
        question = Question.objects.filter(tags__slug=slug)
        
        serializer = QuestionSerializer(question, many=True)
        
        return Response(serializer.data, status.HTTP_200_OK)
    
    
class BestAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, slug, **args):
        question = Question.objects.get(slug=slug)
        
        if request.data.get('answer'):
            
            answer = Answer.objects.get(id=request.data['answer'])
            question.best_answer_id = answer
            question.save()
        
            return Response({'message':'best answer submited'}, status.HTTP_200_OK)
        else:
            return  Response({'message':'answer not specified!'}, status.HTTP_400_BAD_REQUEST)