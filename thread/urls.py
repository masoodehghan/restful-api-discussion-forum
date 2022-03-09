from django.urls import path
from . import views

urlpatterns = [
    path('question', views.QuestionListVIew.as_view(), name='question-list'),
    path('question/create', views.QuestionCreateView.as_view(), name='question-create'),
    path('question/<slug:slug>', views.QuestionDetailView.as_view(), name='question-detail'),
    path('question/<slug:slug>', views.QuestionDetailView.as_view(), name='question-edit'),
    path('question/<slug:slug>', views.QuestionDetailView.as_view(), name='question-delete'),
    
    path('answer/<slug:slug>', views.AnswerDetailView.as_view(), name='answer-create'),
    path('answer/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-delete'),
    path('answer/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-update')
]
