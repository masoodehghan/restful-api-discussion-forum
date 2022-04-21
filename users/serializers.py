import re
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
    point = serializers.SerializerMethodField()
    
    def get_point(self, obj):
        # check if point is none
        if obj.point: 
            return obj.point # its a method in model
        else:
            return 0

    class Meta:
        model = User
        fields = ['url', 'email', 'groups', 'first_name', 'question', 'answers', 'point']
        
        
class PasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    