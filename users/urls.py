from xml.etree.ElementInclude import include
from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)


urlpatterns = [
    path('signup', views.RegisterView.as_view(), name='signup'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/<str:uuid>/', views.UserDetail.as_view(), name='user-detail'),
    path('profile', views.UserProfile.as_view(), name='profile'),
    
    path("user/change-password", views.ChangePasswordView.as_view(), name="change-password"),
]
