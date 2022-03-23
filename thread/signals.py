from turtle import pos
from .models import Question
from django.utils.text import slugify
from django.db.models.signals import post_save

def slugify_title(sender, instance, created, **kwargs):
    question = instance
    question.slug = slugify(question.title)
    

post_save.connect(slugify_title, sender=Question)