from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.QuestionListVIew.as_view(), name='question'),
    path('questions/<slug:slug>/', views.QuestionDetailView.as_view(), name='question-detail'),
    
    path('answer/create/', views.AnswerCreateView.as_view(), name='answer-create'),
    path('answer/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),

    path('tag/<slug:slug>/', views.QuestionListByTagView.as_view(), name='question-list-by-tag'),

    path('vote/create/', views.VoteView.as_view(), name='vote'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard')
    
]
