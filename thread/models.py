from django.conf import settings
from django.db import models
from django.urls import reverse


class Question(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    slug = models.SlugField(max_length=50, null=True, blank=True, unique=True)
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='question')
    
    id = models.BigAutoField(primary_key=True, unique=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True)
    
    tags = models.ManyToManyField('Tag', blank=True, related_name='questions')
    best_answer_id = models.OneToOneField(
        'Answer', on_delete=models.CASCADE, null=True, blank=True, related_name='best_answer'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question-detail', kwargs={'slug': self.slug})
    

class Answer(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='answers'
    )

    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    
    content = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    
    @property
    def get_voters(self):
        query_set = self.vote.all().values('owner')
        return query_set
    
    def __str__(self):
        return self.content[:40]

    def get_absolute_url(self):
        return reverse('answer-detail', kwargs={'pk': self.id})
    
    
class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('question-list-by-tag', kwargs={'slug': self.slug})
    

class Vote(models.Model):
    class Values(models.IntegerChoices):
        UP_VOTE = 1

    value = models.IntegerField(choices=Values.choices)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='vote', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, related_name='votes')

    def __str__(self):
        return f"{str(self.value)}    {self.answer.content}"
