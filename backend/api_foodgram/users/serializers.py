from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

User = get_user_model()


error_message = 'Длина не может превышать 150 символов'


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        fields = (
            "email", "username", "first_name",
            "last_name", "password",
        )
        model = User

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                {'email': 'Длина почты не может превышать 254 символа'}
            )
        return value

    def validate_username(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                {'username': error_message}
            )
        return value

    def validate_password(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                {'password': error_message}
            )
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                {'last_name': error_message}
            )
        return value

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                {'first_name', error_message}
            )
        return value
