FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN adduser forum_admin --disabled-password
RUN su forum_admin

WORKDIR /home/forum_admin/django-forum
COPY --chown=user:forum_admin requirements.txt requirements.txt
RUN pip install -r requirements.txt
USER forum_admin


COPY --chown=user:forum_admin src /home/forum_admin/django-forum/



