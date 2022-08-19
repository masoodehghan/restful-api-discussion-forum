from forum.celery import app
from .util import send_password_reset_to_user
import os
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


@app.task(name='send_reset_password_email')
def send_reset_password_email(
        user_email, uid, token, domain='127.0.0.1:8000', use_https=False):

    protocol = 'https' if use_https else 'http'
    url = reverse(
        'v1:password_reset_confirm',
        kwargs={
            'uid': uid,
            'token': token})
    domain = 'localhost' if os.environ.get('USING_NGINX') else domain

    message = f'{protocol}://{domain}{url}'

    subject = 'email to reset password'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email]
    )
