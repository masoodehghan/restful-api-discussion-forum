from rest_framework import serializers
import django.contrib.auth.password_validation as validator
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .util import send_password_reset_to_user
from .tasks import send_reset_password_email


UserModel = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=100,
        required=True,
        write_only=True,
        validators=[validator.validate_password])
    password2 = serializers.CharField(max_length=100, required=True, write_only=True)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'password',
                  'password2', 'first_name', 'last_name', 'uuid']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords are not equal')
        data.pop('password2')

        return super(RegisterSerializer, self).validate(data)

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(slug_field='slug', many=True, read_only=True)
    url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'first_name', 'last_name', 'question', 'point', 'url']
        read_only_fields = ['point', 'email']


class LeaderboardSerializer(serializers.Serializer):
    point = serializers.IntegerField(min_value=0, read_only=True)
    best_answer_count = serializers.IntegerField(min_value=0, read_only=True)
    username = serializers.CharField(max_length=150, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'first_name', 'last_name',
                  'point', 'pk']
        read_only_fields = ['email', 'point', 'username']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=True)

    def _authenticate(self, **credential):
        return authenticate(self.context['request'], **credential)

    def _validate_username(self, username, password):
        if username and password:
            user = self._authenticate(username=username, password=password)
            return user
        else:
            raise serializers.ValidationError('username is required')

    def get_auth_user(self, email, username, password):
        if email:
            try:
                username = UserModel.objects.get(email__iexact=email).get_username()
            except UserModel.DoesNotExist:
                pass

        user = self._validate_username(username, password)
        return user

    def validate(self, attr):
        username = attr.get('username')
        email = attr.get('email')
        password = attr.get('password')

        user = self.get_auth_user(email, username, password)

        if user is None:
            raise serializers.ValidationError('cannot login with provided credential')

        if not user.is_active:
            raise serializers.ValidationError('inactive user cant login')

        attr['user'] = user

        return attr


class JWTSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserProfileSerializer(obj['user'], many=False, context=self.context).data


class TokenRefreshCookieSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(required=False, help_text='override from cookie')

    def extract_refresh(self):
        request = self.context['request']

        if 'refresh' in request.data and request.data.get('refresh') != '':
            return request.data['refresh']

        cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)

        if cookie_name and cookie_name in request.COOKIES:
            return request.COOKIES.get(cookie_name)
        else:
            from rest_framework_simplejwt.exceptions import InvalidToken
            raise InvalidToken('refresh token is not valid')

    def validate(self, attrs):
        attrs['refresh'] = self.extract_refresh()
        return super().validate(attrs)


class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=32, write_only=True, style={'input_type': 'password'},
                                     validators=[validator.validate_password])

    password2 = serializers.CharField(max_length=32, write_only=True, style={'input_type': 'password'})
    old_password = serializers.CharField(max_length=32, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        self.instance = self.context['request'].user

        if not self.instance.check_password(attrs['old_password']):
            raise serializers.ValidationError('incorrect old password.')

        return super().validate(attrs)

    def save(self, **kwargs):
        self.instance.set_password(self.validated_data['password'])
        self.instance.save()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100, write_only=True)

    def validate(self, attrs):
        try:
            attrs['user'] = UserModel.objects.get(email=attrs['email'])

        except UserModel.DoesNotExist:
            raise serializers.ValidationError('enter valid email')

        return attrs

    def save(self, **kwargs):
        request = self.context.get('request')
        uid = urlsafe_base64_encode(force_bytes(self.validated_data['user'].pk))
        token = default_token_generator.make_token(self.validated_data['user'])

        send_reset_password_email.delay(
            user_email=self.validated_data['email'],
            uid=uid,
            token=token,
            use_https=request.is_secure()
        )


class PasswordResetCompleteSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(write_only=True, validators=[validator.validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError('passwords are not match')
        try:
            self.instance = UserModel.objects.get(pk=force_str(urlsafe_base64_decode(attrs['uid'])))
        except BaseException:
            raise serializers.ValidationError('incorrect uid')

        if not default_token_generator.check_token(self.instance, attrs['token']):
            raise serializers.ValidationError('invalid token')

        return attrs

    def save(self, **kwargs):
        self.instance.set_password(self.validated_data['new_password'])
        self.instance.save()
