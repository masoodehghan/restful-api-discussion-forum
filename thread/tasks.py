from forum.celery import app
from .email import send_answer_email
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(name='send_email_to_question_owner', max_retries=5)
def send_email_to_question_owner_task(owner_name, owner_email,
                                      answer_content, answer_owner_username):

    logger.info('Email sent successfully')
    return send_answer_email(owner_name, owner_email, answer_content, answer_owner_username)
