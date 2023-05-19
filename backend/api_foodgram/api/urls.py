from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view()),
    path('recipes/{id}/shopping_cart/', ShoppingCartViewSet.as_view()),
    path('recipes/{id}/favorite', FavoriteViewSet.as_view()),
    path('', include(router.urls)),
]
