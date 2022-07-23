from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_answer_email(question_owner_name, question_owner_email,
                      answer_content, answer_owner_username):

    context = {
        'name': question_owner_name,
        'email': question_owner_email,
        'answer_content': answer_content,
        'answer_owner': answer_owner_username
    }

    email_subject = 'Answer submitted to your question'
    email_body = render_to_string('email_message.txt', context)

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [question_owner_email, ]
    )

    return email.send()

