from django.contrib.auth.backends import ModelBackend
import re
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class UsernameOrEmailModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if re.fullmatch(regex, username):
            kwargs = {'email': username}

        else:
            kwargs = {'username': username}

        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user

        except get_user_model().DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None


class JWTCookieAuthentication(JWTAuthentication):

    def authenticate(self, request):
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)

        header = self.get_header(request)
        if header is None:
            if cookie_name:
                raw_token = request.COOKIES.get(cookie_name)

            else:
                return None

        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
