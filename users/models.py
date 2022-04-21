from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from thread.models import Vote


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=300)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    
    @property
    def point(self):
        answer = self.answers.all()
        votes = Vote.objects.filter(answer__in=answer).aggregate(models.Sum('value'))
        return votes.get('value__sum')
        
        
    
    
