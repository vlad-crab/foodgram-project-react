from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.serializers import ReducedRecipeSerializer


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
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


class UsersWithRecipesSerializer(UsersSerializer):
    recipes = ReducedRecipeSerializer(many=True, read_only=True)

    class Meta:
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "recipes", 'is_subscribed',
        )
        model = User
