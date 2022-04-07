from turtle import pos
from .models import Question, Tag
from django.utils.text import slugify
from django.db.models.signals import pre_save

def slugify_title(sender, instance, *args, **kwargs):
    instance.slug = create_unique_slug('Question', instance)

def slugify_name_tag(sender, instance, *args, **kwargs):
    instance.slug = create_unique_slug('Tag', instance)  
    

def create_unique_slug(obj, instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        if obj == 'Tag':
            slug = slugify(instance.name)
        elif obj == 'Question':
            slug = slugify(instance.title)
    
    instanceClass = instance.__class__
    query_set = instanceClass.objects.filter(slug=slug)
    
    if query_set.exists():
        new_slug = f"{slug}-{query_set.first().id}"
        return create_unique_slug(obj, instance, new_slug)
    
    return slug


pre_save.connect(slugify_title, sender=Question)
pre_save.connect(slugify_name_tag, sender=Tag)
