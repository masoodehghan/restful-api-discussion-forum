from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters


def jwt_encode(user):
    refresh = RefreshToken.for_user(user)

    return str(refresh), str(refresh.access_token)


def set_cookie_jwt_access(response, access_token):
    acc_cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    acc_expire_time = timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']

    if acc_cookie_name:
        response.set_cookie(
            acc_cookie_name,
            access_token,
            expires=acc_expire_time,
            samesite='Lax'
        )


def set_cookie_jwt_refresh(response, refresh_token):

    refresh_cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
    refresh_expire_time = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

    if refresh_cookie_name:
        response.set_cookie(
            refresh_cookie_name,
            refresh_token,
            expires=refresh_expire_time,
            samesite='Lax'
        )


def set_cookie_jwt(response, access_token, refresh_token):
    set_cookie_jwt_access(response, access_token)
    set_cookie_jwt_refresh(response, refresh_token)


def unset_cookie_jwt(response):
    acc_cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    refresh_cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)

    if acc_cookie_name:
        response.delete_cookie(acc_cookie_name)

    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name)


def send_password_reset_to_user(user_email, uid, token, domain='127.0.0.1:8000', use_https=False):
    protocol = 'https' if use_https else 'http'
    url = reverse('v1:password_reset_confirm', kwargs={'uid': uid, 'token': token})
    message = f'{protocol}://{domain}{url}'

    subject = 'email to reset password'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email]
    )


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password2', 'new_password', 'new_password2', 'old_password')
)
