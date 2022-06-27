from rest_framework import serializers
from .models import Answer, Question, Tag, Vote
from django.contrib.auth import get_user_model
from django.db.models import F


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ['owner']

    def to_representation(self, instance):
        ret = super(AnswerSerializer, self).to_representation(instance)
        ret['owner'] = instance.owner.username
        ret.pop('question')
        return ret
    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['slug']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(source='answer_set', many=True, read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'answers', 'slug']

    def update(self, instance, validated_data):
        if validated_data.get('best_answer_id'):
            answer = validated_data['best_answer_id']

            user_objs = [answer.owner, instance.owner]

            if user_objs[0] == user_objs[1]:
                raise serializers.ValidationError('Your own answer cant be the best answer')

            user_objs[0].point = F('point') + 10
            user_objs[1].point = F('point') + 2

            get_user_model().objects.bulk_update(user_objs, ['point'])

        return super(QuestionSerializer, self).update(instance, validated_data)


class QuestionMiniSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Question
        exclude = ['best_answer_id']
        read_only_fields = ['url', 'owner', 'slug']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
