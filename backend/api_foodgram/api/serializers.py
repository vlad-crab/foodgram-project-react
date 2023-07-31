import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, IngredientWithWT, Recipe, Tag

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class ReducedRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class IngredientWithWTSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = IngredientWithWT


class UsersWithRecipesSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'recipes', 'is_subscribed',
            'recipes_count'
        )
        model = User
        read_only_fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'recipes', 'is_subscribed',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.following.filter(user=user).exists()

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return ReducedRecipeSerializer(queryset, many=True).data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=False
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def get_ingredients(self, obj):
        query = IngredientWithWT.objects.filter(
            recipe=obj
        ).select_related('ingredient')
        serializer = IngredientWithWTSerializer(query, many=True)
        return serializer.data


class IngredientForRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientForRecipeWriteSerializer(
        many=True, write_only=True
    )

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

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe(**validated_data, author=author)
        recipe.save()
        ingredient_wt_obj_list = []
        for ingredient in ingredients:
            ingredient_wt_obj_list.append(
                IngredientWithWT(
                    ingredient_id=ingredient['id'],
                    recipe_id=recipe.id,
                    amount=ingredient['amount'],
                )
            )
        IngredientWithWT.objects.bulk_create(
            ingredient_wt_obj_list
        )
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        if 'image' in validated_data.keys():
            instance.image = validated_data['image']
        ingredient_wt_obj_list = []
        IngredientWithWT.objects.filter(recipe__exact=instance).delete()
        for ingredient in ingredients:
            ingredient_wt_obj_list.append(
                IngredientWithWT(
                    ingredient_id=ingredient['id'],
                    recipe=instance,
                    amount=int(ingredient['amount'])
                )
            )
        IngredientWithWT.objects.bulk_create(
            ingredient_wt_obj_list
        )
        instance.tags.set(tags)
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
                    (f'Количество '
                     f'{Ingredient.objects.get(pk=ingredient["id"]).name} '
                     f'не может быть меньше 1')
                )
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(set(ingredient_ids)) != Ingredient.objects.filter(
            id__in=ingredient_ids
        ).count():
            raise serializers.ValidationError(
                'Добавлен ингридиент с несуществующим id'
            )
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один тег'
            )
        return value


class UserCreateSerializer(DjoserCreateSerializer):

    class Meta:
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password',
        )
        model = User
