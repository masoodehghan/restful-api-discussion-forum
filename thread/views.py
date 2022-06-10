from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AnswerSerializer, QuestionSerializer, TagSerializer, VoteSerializer
from .models import Answer, Question
from rest_framework import permissions, status, generics
from .permissions import IsOwner, CustomIsAdminUser
from django.db.models import Q

   
class QuestionListVIew(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, **kwargs):
        
        q = ''   # q is search query

        if request.GET.get('q'):
            q = request.GET.get('q')

        question = Question.objects.distinct().filter(
                                            Q(title__icontains=q) | 
                                            Q(tags__name__icontains=q) | 
                                            Q(owner__first_name__icontains=q) | 
                                            Q(owner__email__icontains=q))

        serializer = QuestionSerializer(question, many=True)
        
        return Response(serializer.data)


class QuestionCreateView(generics.CreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer

    lookup_field = 'slug'
    queryset = Question.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [permissions.AllowAny]

        else:
            permission_classes = [IsOwner]
        return [permission() for permission in permission_classes]


class AnswerDetailView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Answer.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        question = get_object_or_404(Question, slug=self.kwargs['slug'])
        serializer.save(question=question)


class TagView(generics.CreateAPIView):

    """
    only admins can add tag.
    """

    serializer_class = TagSerializer
    permission_classes = [CustomIsAdminUser]


class BestAnswerView(APIView):
    permission_classes = [IsOwner]
    
    def put(self, request, slug, answer_pk, **kwargs):
        question = get_object_or_404(Question, slug=slug)
        
        self.check_object_permissions(request, question)        

        answer = get_object_or_404(Answer, id=answer_pk)
        if question.owner == answer.owner:
            return Response({'message': 'your answer cant be best answer '}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        question.best_answer_id = answer
        answer.owner.point += 10
        question.owner.point += 2

        answer.owner.save()
        question.save()
        question.owner.save()
        
        return Response({'message': 'best answer submited'}, status.HTTP_200_OK)
        

class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, answer_pk, *args, **kwargs):
        
        answer = get_object_or_404(Answer, id=answer_pk)
        data = {'value': int(request.data['value'])}
        serializer = VoteSerializer(data=data)
        
        if answer.voters.exists():

            # check if user already vote or not

            if request.user.id in answer.voters[0].values():
                return Response({'message': 'you already voted!'}, status.HTTP_400_BAD_REQUEST)
        
        if answer.owner == request.user:
            return Response({'message': 'you cant vote your own answer'}, status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(owner=request.user, answer=answer)
            
            return Response({'message': 'vote submited succsessfully.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
