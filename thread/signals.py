from random import choice
from .models import Question, Tag
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save
from string import ascii_lowercase


@receiver(pre_save, sender=Question)
def slugify_title(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(sender.__name__, instance)
    elif instance.title != sender.objects.get(id=instance.id).title:
        instance.slug = create_unique_slug(sender.__name__, instance)


@receiver(pre_save, sender=Tag)
def slugify_name_tag(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(sender.__name__, instance)
    elif instance.name != sender.objects.get(id=instance.id).name:
        instance.slug = create_unique_slug(sender.__name__, instance)
    

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
        random_str = ''.join(choice(ascii_lowercase) for _ in range(5))
        
        new_slug = f"{slug}-{random_str}"
        return create_unique_slug(obj, instance, new_slug)
    
    return slug
