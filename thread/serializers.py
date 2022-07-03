from rest_framework import serializers
from .models import Answer, Question, Tag, Vote
from django.db.models import F


class AnswerSerializer(serializers.ModelSerializer):

    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'

    def to_representation(self, instance):
        ret = super(AnswerSerializer, self).to_representation(instance)
        ret.pop('question')
        return ret


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['slug']


class QuestionSerializer(serializers.ModelSerializer):

    answers = AnswerSerializer(many=True, read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'slug', 'answers']

    def update(self, instance, validated_data):
        if validated_data.get('best_answer'):
            answer = validated_data['best_answer']

            if answer in instance.answers.all():
                if answer.owner_id == instance.owner_id:
                    raise serializers.ValidationError('Your own answer cant be the best answer')

                answer.owner.point = F('point') + 10
                answer.owner.save()

            else:
                raise serializers.ValidationError('answer doesnt belong to your question')

        return super().update(instance, validated_data)


class QuestionMiniSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Question
        exclude = ['best_answer']
        read_only_fields = ['url', 'owner', 'slug']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
