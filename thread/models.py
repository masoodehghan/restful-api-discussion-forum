from django.conf import settings
from django.db import models
from django.urls import reverse

class Question(models.Model):
    title = models.CharField(max_length=50, unique=True)
    body = models.TextField()
    slug = models.SlugField(max_length=50, null=True, blank=True)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='question')
    
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True)
    
    best_answer_id = models.OneToOneField('Answer', 
                                          on_delete=models.CASCADE, 
                                          null=True, 
                                          blank=True, 
                                          related_name='best_answer')
    
    
    def __str__(self):
        return self.title
    

class Answer(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                blank=True, related_name='answers')
    
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.content[:40]
    
    def get_absolute_url(self):
        return reverse("answer-detail", kwargs={"pk": self.id})
    
    