from random import choice
from .models import Question, Tag
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import pre_save
from string import ascii_lowercase, digits


@receiver(pre_save, sender=Question)
def slugify_title(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(instance.title)


@receiver(pre_save, sender=Tag)
def slugify_name_tag(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_unique_slug(instance.name)


def create_unique_slug(obj: str):
    slug = slugify(obj)

    random_str = ''.join(choice(ascii_lowercase + digits) for _ in range(3))

    res_slug = f"{slug}-{random_str}"

    return res_slug
