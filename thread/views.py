from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AnswerSerializer, QuestionSerializer, TagSerializer, VoteSerializer
from .models import Answer, Question
from rest_framework import permissions, status
from .permissions import IsOwnerOrReadOnly, CustomIsAdminUser
from django.db.models import Q

   
class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, **kwargs):
        
        q = ''   # q is serach query

        if request.GET.get('q'):
            q = request.GET.get('q')
        
        
        question = Question.objects.distinct().filter(
                                            Q(title__icontains=q) | 
                                            Q(tags__name__icontains=q) | 
                                            Q(owner__first_name__icontains=q) | 
                                            Q(owner__email__icontains=q))
        
        
        serializer = QuestionSerializer(question, many=True)
        
        return Response(serializer.data)
    
class QuestionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, **kwargs):
        serializer = QuestionSerializer(data=request.data)
        
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
        
    
    def get(self, request, slug, **kwargs):
        qusetion = self.get_object(slug=slug)
        serializer = QuestionSerializer(qusetion, many=False)
        
        return Response({
        'data': serializer.data,
    })
    
    def put(self, request, slug, **kwargs):
        question = self.get_object(slug)
        self.check_object_permissions(request, question)
        
        serializer = QuestionSerializer(instance=question, data=request.data, many=False)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, **kwargs):
        question = self.get_object(slug)
        self.check_object_permissions(request, question)
        question.delete()
        return Response({'message':'question deleted!'}, status.HTTP_204_NO_CONTENT)
    

class AnswerDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated,
                          IsOwnerOrReadOnly]
    
    

    def post(self, request, slug, **kwargs):
        question = get_object_or_404(Question, slug=slug)
        
        serializer = AnswerSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(question=question, owner=request.user)
            request.user.point += 2
            
            request.user.save()
            
            return Response({
                'data':serializer.data,
                'message':'answer created!'
                }, status.HTTP_201_CREATED)
            
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        
    def delete(self, request, pk, **kwargs):
        answer = get_object_or_404(Answer, id=pk)
        self.check_object_permissions(request, answer)
        answer.delete()
        
        return Response({'message':'answer deleted.'}, status.HTTP_204_NO_CONTENT)
    
    
    def put(self, request, pk, **kwargs):
        answer = get_object_or_404(Answer, id=pk)
        self.check_object_permissions(request, answer) # check if owner is updating answer or not
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
                          
    
    def post(self, request, **kwargs):
        
        """
        only admins can add tag
        """
        self.check_permissions(request=request)
        serializer = TagSerializer(data=request.data, many=False)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Tag created.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, slug, **kwargs):
        """
        diplay a list of question by thier tags       
        """
        
        question = Question.objects.filter(tags__slug=slug)
        
        serializer = QuestionSerializer(question, many=True)
        
        return Response(serializer.data, status.HTTP_200_OK)
    
    
class BestAnswerView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    
    def put(self, request, slug, answer_pk, **kwargs):
        question = get_object_or_404(Question, slug=slug)
        
        self.check_object_permissions(request, question)        

        answer = get_object_or_404(Answer, id=answer_pk)
        if question.owner == answer.owner:
            return Response({'message':'your answer cant be best answer '}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        question.best_answer_id = answer
        answer.owner.point += 10
        question.owner.point += 2
        print('DU', answer.owner.point)
        
        answer.owner.save()
        question.save()
        question.owner.save()
        
        return Response({'message':'best answer submited'}, status.HTTP_200_OK)
        

class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def post(self, request, answer_pk, *args, **kwargs):
        
        answer = get_object_or_404(Answer, id=answer_pk)
        data = {'value':int(request.data['value'])}
        serializer = VoteSerializer(data=data)
        
        if answer.voters.exists():
            #check if user already vote or not
            
            if request.user.id in answer.voters[0].values():
                return Response({'message':'you already voted!'}, status.HTTP_400_BAD_REQUEST)
        
        if answer.owner == request.user:
            return Response({'message':'you cant vote your own answer'}, status.HTTP_400_BAD_REQUEST)
        
        
        if serializer.is_valid():
            serializer.save(owner=request.user, answer=answer)
            
            return Response({'message':'vote submited succsessfully.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)