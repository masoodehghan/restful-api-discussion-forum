from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from thread.models import Vote


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=300)
    username = None
    point = models.IntegerField(default=0, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    
        
        
    
    
