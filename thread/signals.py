import random
from .models import Question, Tag, Vote
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

@receiver(pre_save, sender=Question)
def slugify_title(sender, instance, *args, **kwargs):
    instance.slug = create_unique_slug('Question', instance)

@receiver(pre_save, sender=Tag)
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
        random_list = random.sample(range(97, 123), 7)
        random_str = ''.join(map(chr, random_list))
        
        new_slug = f"{slug}-{random_str}"
        return create_unique_slug(obj, instance, new_slug)
    
    return slug

@receiver(post_save, sender=Vote)
def point_to_user(sender, instance, *args, **kwargs):
    answer_owner = instance.answer.owner
    answer_owner.point += 5
    answer_owner.save()
    
    