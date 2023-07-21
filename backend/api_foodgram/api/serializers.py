from rest_framework import serializers
from django.contrib.auth import get_user_model
import base64
from django.core.files.base import ContentFile

from .models import *
from users.serializers import CustomUserSerializer


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measure_unit')
        model = Ingredient


class ReducedRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class IngredientWithWTSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    measure_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'amount', 'name', 'measure_unit')
        model = IngredientWithWT

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measure_unit(self, obj):
        return obj.ingredient.measure_unit


class UsersWithRecipesSerializer(CustomUserSerializer):
    recipes = ReducedRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)


    class Meta:
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "recipes", 'is_subscribed',
            "recipes_count"
        )
        model = User
        read_only_fields = (
            "email", "id", "username", "first_name",
            "last_name", "recipes", 'is_subscribed',
            "recipes_count"
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = IngredientWithWTSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.users_carts.filter(user=user).exists()


class IngredientForRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(many=True, write_only=True)

    class Meta:
        fields = (
            'tags', 'ingredients', 'name', 'author',
            'image', 'text', 'cooking_time', 'id'
        )
        model = Recipe

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe['tags'] = TagSerializer(instance.tags.all(), many=True).data
        recipe['ingredients'] = IngredientWithWTSerializer(
            instance.ingredients.all(), many=True
        ).data
        return recipe


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=author)
        tag_ids = [tag for tag in tags]
        recipe.tags.set(tag_ids)
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(
                id=int(ingredient['id'])
            )
            ingredient_wt_obj = IngredientWithWT.objects.create(
                ingredient=ingredient_obj,
                amount=int(ingredient['amount']),
            )
            recipe.ingredients.add(ingredient_wt_obj)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        if 'image' in validated_data.keys():
            instance.image = validated_data['image']
        tag_ids = [tag_id for tag_id in tags]
        instance.tags.set(tag_ids)
        IngredientWithWT.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            instance.ingredients.add(
                IngredientWithWT.objects.create(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    amount=int(ingredient['amount'])
                )
            )
        instance.save()
        return instance

    def validate_name(self, value):
        if len(value) > 200:
            raise serializers.ValidationError(
                'Название рецепта не может быть длиннее 200 символов'
            )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1 минуты'
            )
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент'
            )
        for ingredient in value:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    'Ингредиент не найден'
                )
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег'
            )
        return value
