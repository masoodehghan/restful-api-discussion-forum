from rest_framework import serializers
from .models import Answer, Question, Tag, Vote
from users.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Answer
        fields = '__all__'
    
    def get_owner(self, obj):
        serialize = UserSerializer(obj.owner, many=False, context={'request':None})
        return serialize.data['email']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
   
    
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id']
        
    def get_owner(self, obj):
        serialize = UserSerializer(obj.owner, many=False, context={'request':None})
        return serialize.data['email']
     
    def get_answers(self, obj):
        answer = obj.answer_set.all()
        seriaize = AnswerSerializer(answer, many=True)
        return seriaize.data

           
class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'            
    
        
        