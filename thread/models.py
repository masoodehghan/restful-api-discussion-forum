
from django.db import models
from users.models import User

class Question(models.Model):
    title = models.CharField(max_length=50, unique=True)
    body = models.TextField()
    slug = models.SlugField(max_length=50, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='question')
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.title
    
    