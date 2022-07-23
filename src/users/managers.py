from django.contrib.auth.backends import ModelBackend
import re
from django.contrib.auth import get_user_model


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
