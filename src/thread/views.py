from django.shortcuts import get_object_or_404
from .serializers import (
    AnswerSerializer, QuestionRetrieveSerializer, QuestionUpdateSerializer,
    VoteSerializer, QuestionListCreateSerializer)

from .models import Answer, Question, Vote, Tag
from rest_framework import permissions, generics, versioning
from .permissions import IsOwner
from rest_framework.filters import SearchFilter
from django.db.models import Prefetch, Count
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator
from users.serializers import LeaderboardSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_404_NOT_FOUND
from .tasks import send_email_to_question_owner_task


class QuestionListVIew(generics.ListCreateAPIView):

    serializer_class = QuestionListCreateSerializer
    versioning_class = versioning.NamespaceVersioning
    filter_backends = [SearchFilter]
    search_fields = ['title', 'tags__name', 'owner__username']

    def get_queryset(self):
        fields = [
            'slug',
            'body',
            'tags',
            'create_time',
            'title',
            'owner__username',
            'tags__id']

        queryset = Question.objects.select_related('owner')\
            .prefetch_related('tags').order_by('-create_time')

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
    #     serializer = QuestionRetrieveSerializer(question, many=True)
    #
    #     return Response(serializer.data)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwner]

    lookup_field = 'slug'
    _object = None

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QuestionUpdateSerializer

        else:
            return QuestionRetrieveSerializer

    def get_queryset(self):

        answers = Answer.objects.select_related('owner').only(
            'content', 'owner__username', 'created', 'question')

        fields = ['tags__name', 'owner__username', 'title',
                  'body', 'slug', 'create_time', 'best_answer']

        queryset = Question.objects.select_related(
            'owner').prefetch_related(Prefetch('answers', answers))

        return queryset.only(*fields)

    # @method_decorator(cache_page(60*2))  # cache page for 2 minutes
    # @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        self._object = super().get_object()
        return self._object

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.path != '/api/v1/docs/':
            context['question_id'] = self._object.id
        return context


class AnswerCreateView(generics.CreateAPIView):
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        question_owner = instance.question.owner

        if instance.owner_id != question_owner.id:

            send_email_to_question_owner_task.delay(
                question_owner.username,
                question_owner.email,
                instance.content,
                instance.owner.username)


class AnswerDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Answer.objects.all()


class QuestionListByTagView(generics.ListAPIView):
    serializer_class = QuestionListCreateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        fields = [
            'slug',
            'body',
            'tags',
            'create_time',
            'title',
            'owner__username',
            'tags__id']

        tags = get_object_or_404(Tag, slug=self.kwargs['slug'])

        queryset = Question.objects.select_related(
            'owner').prefetch_related('tags')

        return queryset.filter(tags=tags).only(*fields)


class VoteView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = []

    def get_queryset(self):
        user_queryset = get_user_model().objects.only('username', 'point')
        queryset = user_queryset.annotate(
            best_answer_count=Count('answers_owner__best_answer_id'))

        return queryset.order_by('-point')

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
