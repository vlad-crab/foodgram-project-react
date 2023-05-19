from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from .serializers import *
from .permissions import IsAuthenticated, IsAuthorOrReadOnly
from .models import *
from .filters import RecipeFilter


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
    queryset = Ingredient.objects.all()


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
        ShoppingCart.objects.get_or_create(
            user=self.request.user,
            recipe=recipe
        )
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


    def perform_destroy(self, request):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        ).delete()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = ReducedRecipeSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perfom_create(self, request):
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        Favorite.objects.get_or_create(
            user=self.request.user,
            recipe=recipe
        )
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    def perform_destroy(self, request):
        obj = Favorite.objects.filter(
            user=self.request.user,
            recipe=self.kwargs['pk']
            )
        if not obj.exists():
            return Response(status=404, data={'errors': 'Not found'})
        obj.delete()



class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthorOrReadOnly, ]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filterset_fields = ('tags', 'is_favorited', 'is_in_shopping_cart')
    filter_backends = (DjangoFilterBackend, )
