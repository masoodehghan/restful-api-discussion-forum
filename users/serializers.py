
from .models import User
from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        
class UserSerializer(serializers.HyperlinkedModelSerializer):
    question = serializers.SlugRelatedField(slug_field='slug', many=True, read_only=True)
    answers = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    
    class Meta:
        model = User
        fields = ['url', 'email', 'groups', 'first_name', 'question', 'answers']
        
        
class PasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    