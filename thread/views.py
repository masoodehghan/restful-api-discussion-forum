from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (AnswerSerializer, QuestionSerializer,
                          TagSerializer, VoteSerializer, QuestionMiniSerializer)
from .models import Answer, Question
from rest_framework import permissions, status, generics
from .permissions import IsOwner
from rest_framework.filters import SearchFilter
from django.db.models import Prefetch, F


class QuestionListVIew(generics.ListCreateAPIView):

    serializer_class = QuestionMiniSerializer

    filter_backends = [SearchFilter]
    search_fields = ['title', 'tags__name', 'owner__username']

    def get_queryset(self):
        fields = [
            'slug', 'body', 'tags', 'create_time', 'title', 'owner__username', 'tags__id'
        ]
        queryset = Question.objects.select_related('owner').prefetch_related('tags').order_by('-create_time')

        return queryset.only(*fields)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def get(self, request, **kwargs):
    #
    #     q = ''   # q is search query
    #
    #     if request.GET.get('q'):
    #         q = request.GET.get('q')
    #
    #     question = Question.objects.distinct().filter(
    #                                         Q(title__icontains=q) |
    #                                         Q(tags__name__icontains=q) |
    #                                         Q(owner__username__icontains=q))
    #
    #     serializer = QuestionSerializer(question, many=True)
    #
    #     return Response(serializer.data)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsOwner]

    lookup_field = 'slug'

    def get_queryset(self):

        answers = Answer.objects.select_related('owner').only('content', 'owner__username',
                                                              'created', 'question', 'is_best')

        fields = ['tags__name', 'owner__username', 'title',
                  'body', 'slug', 'create_time', 'best_answer_id']

        queryset = Question.objects.prefetch_related(Prefetch('answer_set', answers))

        return queryset.only(*fields)


class AnswerCreateView(generics.CreateAPIView):
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):

        serializer.save(owner=self.request.user)


class AnswerDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Answer.objects.all()


class TagView(generics.CreateAPIView):

    """
    only admins can add tag.
    """

    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]


class QuestionListByTagView(generics.ListAPIView):
    serializer_class = QuestionMiniSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        fields = [
            'slug', 'body', 'tags', 'create_time', 'title', 'owner__username', 'tags__id'
        ]

        queryset = Question.objects.select_related('owner').prefetch_related('tags')
        return queryset.filter(tags__slug=self.kwargs['slug']).only(*fields)


class VoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, answer_pk, *args, **kwargs):

        answer = get_object_or_404(Answer, id=answer_pk)
        data = {'value': int(request.data['value'])}
        serializer = VoteSerializer(data=data)
        user = request.user
        if answer.get_voters.exists():

            # check if user already vote or not

            if user.id in answer.get_voters[0].values():
                return Response({'message': 'you already voted!'}, status.HTTP_400_BAD_REQUEST)
        
        if answer.owner == user:
            return Response({'message': 'you cant vote your own answer'}, status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(owner=user, answer=answer)

            user.point = F('point') + 5
            user.save()
            
            return Response({'message': 'vote submitted successfully.'}, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
