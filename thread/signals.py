from turtle import pos
from .models import Question
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save

def slugify_title(sender, instance, *args, **kwargs):
    question = instance
    question.slug = create_unique_slug(instance)
    

def create_unique_slug(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)
    
    instanceClass = instance.__class__
    query_set = instanceClass.objects.filter(slug=slug)
    
    if query_set.exists():
        new_slug = f"{slug}-{query_set.first().id}"
        return create_unique_slug(instance, new_slug)
    
    return slug


pre_save.connect(slugify_title, sender=Question)