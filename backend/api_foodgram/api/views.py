from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import *
from .permissions import IsAuthenticated, IsAuthorOrReadOnly
from .models import *
from .filters import RecipeFilter


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()
    permission_classes = (permissions.AllowAny, )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    queryset = Tag.objects.all()


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ReducedRecipeSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def perform_retrieve(self, request):
        user = self.request.user
        recipe_ids = [obj.recipe.id for obj in ShoppingCart.objects.filter(user=user)]
        queryset = IngredientWithWT.objects.filter(recipe__in=recipe_ids).values(
            'ingredient').annotate(amount=Sum('amount'))
        shopping_cart = ''
        for item in queryset:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            shopping_cart += f'{ingredient.name} ({item["amount"]})' \
                             f'{ingredient.measure_unit}, \n'
        response = HttpResponse(shopping_cart, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


    def perform_create(self, request):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        obj = ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if obj.exists():
            return Response(
                {'errors': 'Вы уже добавили рецепт в корзину'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(
            user=self.request.user,
            recipe=recipe
        )
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


    def perform_destroy(self, request):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        obj = ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if not obj.exists():
            return Response(
                {'errors': 'Рецепта не было в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = ReducedRecipeSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        favorite_obj = Favorite.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if favorite_obj.exists():
            return Response(
                {'errors': 'Вы уже добавили рецепт в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(
            user=self.request.user,
            recipe=recipe
        )
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        favorite_obj = Favorite.objects.filter(
            user=self.request.user,
            recipe=self.kwargs['pk']
            )
        if not favorite_obj.exists():
            return Response(
                {'errors': 'Рецепта не было в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthorOrReadOnly, ]
    filterset_class = RecipeFilter
    filterset_fields = ('tags', 'is_favorited', 'is_in_shopping_cart')
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        request = self.request
        if request.query_params.get('is_favorited'):
            queryset = queryset.filter(
                users_favorites__user=user
            )
        if request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(
                users_carts__user=user
            )
        if request.query_params.get('author'):
            queryset = queryset.filter(
                author=request.query_params.get('author')
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer


class ManageSubscriptionsView(viewsets.ViewSet):
    def list(self, request):
        return Response('Эндпоинт доступен')

    def create(self, request, pk):
        return Response('Эндпоинт доступен')

    def destroy(self, request, pk):
        return Response('Эндпоинт доступен')

'''
class ManageSubscriptionsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsersWithRecipesSerializer

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)

    def get_pagination_class(self):
        if self.request.method == 'GET':
            return PageNumberPagination
        return None

    def list(self, request, *args, **kwargs):
        return Response('Эндпоинт доступен')

    def retrieve(self, request, *args, **kwargs):
        return Response('Эндпоинт доступен')

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = request.user
        if author == user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.create(user=user, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = request.user
        if author == user:
            return Response(
                {'errors': 'Нельзя отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Subscriptions.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
'''
