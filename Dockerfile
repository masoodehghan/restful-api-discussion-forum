FROM python:3.10-slim-buster

WORKDIR /django-forum

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ['python' ,'-m' ,'pip' ,'install' ,'--upgrade' ,'pip']

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

