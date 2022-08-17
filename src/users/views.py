from rest_framework import permissions, generics
from rest_framework.views import APIView
from django.contrib.auth import login as session_login, logout

from .util import (
    jwt_encode, set_cookie_jwt, set_cookie_jwt_refresh,
    set_cookie_jwt_access, unset_cookie_jwt, sensitive_post_parameters_m
)
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from .serializers import (
    UserSerializer, JWTSerializer, LoginSerializer, RegisterSerializer,
    PasswordResetSerializer, PasswordChangeSerializer,
    TokenRefreshCookieSerializer, PasswordResetCompleteSerializer, UserProfileSerializer
)
from .models import User
from rest_framework_simplejwt.views import TokenRefreshView


class RegisterView(generics.CreateAPIView):

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def get_response(self, user, access_token, refresh_token, headers):

        data = {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        response_serializer = JWTSerializer(data, context=self.get_serializer_context())
        response = Response(response_serializer.data, status.HTTP_201_CREATED, headers=headers)

        if getattr(settings, 'AUTH_USE_COOKIE', False):
            set_cookie_jwt(response, access_token, refresh_token)

        if getattr(settings, 'SESSION_AUTH', False):
            session_login(self.request, user)

        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        refresh_token, acc_token = jwt_encode(user)

        return self.get_response(user, acc_token, refresh_token, headers)

    def perform_create(self, serializer):
        user = serializer.save()
        return user


class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.defer('password', 'is_active', 'is_staff', 'date_joined')

    lookup_field = 'uuid'


class UserProfile(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = User.objects.defer('password', 'is_active', 'is_staff', 'date_joined')

    def get_object(self):
        return self.request.user


class LoginView(generics.GenericAPIView):

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    refresh_token = None
    access_token = None
    user = None

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.refresh_token, self.access_token = jwt_encode(self.user)

        if getattr(settings, 'SESSION_AUTH', False):
            session_login(self.request, self.user)

    def get_response(self):
        response_data = {'user': self.user,
                         'access_token': self.access_token,
                         'refresh_token': self.refresh_token}

        response_serializer = JWTSerializer(response_data)

        response = Response(response_serializer.data, status=status.HTTP_200_OK)

        if getattr(settings, 'AUTH_USE_COOKIE', False):
            set_cookie_jwt(response, self.access_token, self.refresh_token)

        return response

    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()


class RefreshTokenView(TokenRefreshView):
    serializer_class = TokenRefreshCookieSerializer

    def finalize_response(self, request, response, *args, **kwargs):

        if response.status_code == 200 and 'access' in response.data:
            set_cookie_jwt_access(response, response.data['access'])

        if response.status_code == 200 and 'refresh' in response.data:
            set_cookie_jwt_refresh(response, response.data['refresh'])

        return super().finalize_response(request, response, *args, **kwargs)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):

        response = Response({'detail': 'Logged out successfully'}, status.HTTP_200_OK)
        unset_cookie_jwt(response)

        if getattr(settings, 'SESSION_AUTH', False):
            logout(self.request)

        return response


class PasswordChangeView(generics.GenericAPIView):

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'password changed successfully'}, status.HTTP_200_OK)


class PasswordResetView(generics.GenericAPIView):

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'password reset email sent to you'}, status.HTTP_200_OK)


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer
    permission_classes = [permissions.AllowAny]

    @sensitive_post_parameters_m
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({'detail': 'password change successfully'}, status.HTTP_200_OK)
