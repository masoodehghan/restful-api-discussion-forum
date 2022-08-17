from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('user/<uuid:uuid>/', views.UserDetail.as_view(), name='user-detail'),
    path('profile/', views.UserProfile.as_view(), name='profile'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('token/refresh/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/obtain/', TokenObtainPairView.as_view(), name='obtain_token'),

    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),

    path('password/reset/confirm/<str:uid>/<str:token>/',
         views.ResetPasswordConfirmView.as_view(),
         name='password_reset_confirm'
         ),
]
