from rest_framework import serializers
from .models import Question
from users.serializations import UserSerializer
class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'slug', 'body', 'owner', 'create_time']
        read_only_fields = ['id']
        
        
    def get_owner(self, obj):
        serialize = UserSerializer(obj.owner, many=False, context={'request':None})
        return serialize.data['email']
            
        

        
        