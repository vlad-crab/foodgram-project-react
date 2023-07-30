from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, ShoppingCart,
                            Subscriptions, Tag)

from .filters import InredientNameFilter, RecipeFilter
from .permissions import IsAuthor, ReadOnly
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ReducedRecipeSerializer,
                          TagSerializer, UsersWithRecipesSerializer)
from .services import get_shopping_list

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    filterset_fields = ('name', )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = InredientNameFilter
    queryset = Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny, )
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminUser | IsAuthor | ReadOnly,)
    filterset_class = RecipeFilter
    filterset_fields = (
        'tags', 'is_in_shopping_cart',
        'is_favorited', 'author'
    )
    filter_backends = (DjangoFilterBackend, )

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(
            'tags', 'ingredients', 'author'
        )
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user,
                        recipe=OuterRef('pk')
                    )
                ),
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = get_shopping_list(request.user)
        response = HttpResponse(shopping_cart, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; filename='
                                           '"shopping_cart.txt"')
        return response


class ManageSubscriptionsView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = UsersWithRecipesSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)

    def get_pagination_class(self):
        if self.request.method == 'GET':
            return PageNumberPagination
        return None

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
        del_count, _ = Subscriptions.objects.filter(
            user=user,
            author=author
        ).delete()
        if not del_count:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteShoppingCartMixin(viewsets.ModelViewSet):
    serializer_class = ReducedRecipeSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, ]
    model = None

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        obj = self.model.objects.filter(
            user=user,
            recipe=recipe
        )
        if obj.exists():
            return Response(
                {'errors': 'Уже добавлено'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.model.objects.create(
            user=self.request.user,
            recipe=recipe
        )
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        del_count, _ = self.model.objects.filter(
            user=self.request.user,
            recipe=recipe
        ).delete()
        if not del_count:
            return Response(
                {'errors': 'Нельзя удалить то, чего нет :('},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(FavoriteShoppingCartMixin):
    model = Favorite


class ShoppingCartViewSet(FavoriteShoppingCartMixin):
    model = ShoppingCart
