from rest_framework import serializers
from .models import Answer, Question, Tag, Vote
from users.serializers import UserSerializer


class AnswerSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'
    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    answers = AnswerSerializer(source='answer_set', many=True, read_only=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'answers', 'url']
        

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'            
    
        
        