from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from thread.models import Vote
from uuid import uuid4
from django.urls import reverse


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=300)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    point = models.IntegerField(default=0, blank=True)

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'uuid': self.uuid})
