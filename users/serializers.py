from .models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validator


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, required=True, write_only=True)
    password2 = serializers.CharField(max_length=100, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'uuid']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords are not equal')
        data.pop('password2')
        user = User(**data)
        password = data.get('password')
        errors = dict()

        try:
            validator.validate_password(password=password, user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(RegisterSerializer, self).validate(data)

    def create(self, validated_data):
        print(validated_data)
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(slug_field='slug', many=True, read_only=True)
    answers = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'question', 'answers', 'point', 'url']
        read_only_fields = ['point']


class PasswordSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
