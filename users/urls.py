from django.urls import path
from . import views


urlpatterns = [
    path('user/<uuid:uuid>/', views.UserDetail.as_view(), name='user-detail'),
    path('profile', views.UserProfile.as_view(), name='profile')
]
