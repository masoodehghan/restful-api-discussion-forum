from rest_framework import serializers
from .models import Answer, Question, Tag, Vote
from django.db.models import F
from .signals import create_unique_slug


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
        fields = ['name', 'slug']
        read_only_fields = ['slug']


class QuestionSerializer(serializers.ModelSerializer):

    class BestAnswerField(serializers.PrimaryKeyRelatedField):
        def get_queryset(self):
            return Answer.objects.filter(question=self.context['question_id'])

    best_answer = BestAnswerField(required=False, allow_null=True)
    answers = AnswerSerializer(many=True, read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['owner', 'slug', 'answers']

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])

        self.__update_tags(instance, tags)

        if instance.best_answer is None and validated_data.get('best_answer'):
            answer = validated_data['best_answer']
            self.__best_answer_point(instance, answer)

        return super().update(instance, validated_data)

    @staticmethod
    def __update_tags(instance: Question, validated_tags):

        tags_list = [x['name'] for x in validated_tags]
        if tags_list:
            instance.tags.clear()

            question_tags = instance.tags.values_list('name', flat=True)
            all_tags = Tag.objects.values_list('name', flat=True)
            new_tags = []
            tags_list_b = tags_list.copy()

            for item in tags_list:
                if item not in all_tags:
                    new_tags.append(item)

                if question_tags and item in question_tags:
                    tags_list_b.remove(item)

            tags_list = tags_list_b

            new_created_tags = []
            if new_tags:
                new_created_tags = Tag.objects.bulk_create(
                    Tag(name=tag, slug=create_unique_slug(tag))
                    for tag in new_tags)
            tags = []
            if tags_list:
                tags = Tag.objects.filter(
                    name__in=tags_list).values_list(
                    'id', flat=True)

            instance.tags.add(*tags, *new_created_tags)

    @staticmethod
    def __best_answer_point(instance: Question, answer: Answer):
        if answer in instance.answers.all():

            if answer.owner_id == instance.owner_id:
                raise serializers.ValidationError(
                    'Your own answer cant be the best answer')

            answer.owner.point = F('point') + 10
            answer.owner.save()

        else:
            raise serializers.ValidationError(
                'answer doesnt belong to your question')


class QuestionMiniSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Question
        exclude = ['best_answer']
        read_only_fields = ['url', 'owner', 'slug']

    tags = TagSerializer(many=True, required=False)

    def create(self, validated_data):
        tags_list = [x['name'] for x in validated_data.pop('tags', [])]
        question = Question.objects.create(**validated_data)

        self.__create_tags(question, tags_list)

        return question

    @staticmethod
    def __create_tags(instance: Question, tags_list):
        if tags_list:
            tags_names = Tag.objects.values_list('name', flat=True)

            new_tag = []

            for tag in tags_list:
                if tag not in tags_names:
                    new_tag.append(tag)

            tags = []
            if new_tag:
                tags = [
                    Tag(name=tag_name, slug=create_unique_slug(tag_name))
                    for tag_name in new_tag]
                Tag.objects.bulk_create(tags)

            existed_tags = Tag.objects.filter(
                name__in=tags_list).values_list(
                'id', flat=True)

            instance.tags.add(*tags, *existed_tags)


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        fields = '__all__'
        read_only_fields = ['owner']

    def create(self, validated_data):
        user = self.context['request'].user
        answer = validated_data['answer']
        validated_data['owner'] = user
        if answer.get_voter_ids:

            # check if user already vote or not
            if user.id in answer.get_voter_ids:
                raise serializers.ValidationError('you already voted.')

        if answer.owner == user:
            raise serializers.ValidationError('you cant vote your own answer.')

        user.point = F('point') + 5
        user.save()

        vote = Vote.objects.create(**validated_data)

        return vote
