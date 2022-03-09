from rest_framework import serializers
from .models import Answer, Question
from users.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Answer
        fields = '__all__'
    
    def get_owner(self, obj):
        serialize = UserSerializer(obj.owner, many=False, context={'request':None})
        return serialize.data['email']


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'slug', 'owner', 'create_time', 'answers']
        read_only_fields = ['id']
        
    def get_owner(self, obj):
        serialize = UserSerializer(obj.owner, many=False, context={'request':None})
        return serialize.data['email']
     
    def get_answers(self, obj):
        answer = obj.answer_set.all()
        seriaize = AnswerSerializer(answer, many=True)
        return seriaize.data

            

        
        