from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.reverse import reverse
from .managers import CustomUserManager

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=300)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    
    
