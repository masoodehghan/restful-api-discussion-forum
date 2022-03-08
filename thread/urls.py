from django.urls import path
from . import views

urlpatterns = [
    path('question', views.QuestionListVIew.as_view(), name='question_list'),
    path('question/create', views.QuestionCreateView.as_view(), name='question_create'),
    path('question/<slug:slug>', views.QuestionDetailView.as_view(), name='question-detail')
]
