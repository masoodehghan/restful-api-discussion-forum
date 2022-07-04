from django.urls import path
from . import views

urlpatterns = [
    path('question', views.QuestionListVIew.as_view(), name='question'),
    path('question/<slug:slug>', views.QuestionDetailView.as_view(), name='question-detail'),
    
    path('answer/create', views.AnswerCreateView.as_view(), name='answer-create'),
    path('answer/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),
    
    path('tag/create', views.TagView.as_view(), name='tag-create'),
    path('tag/<slug:slug>', views.QuestionListByTagView.as_view(), name='question-list-by-tag'),

    path('vote/<int:answer_pk>/', views.VoteView.as_view(), name='vote'),
    path('leaderboard', views.LeaderboardView.as_view(), name='leaderboard')
    
]
