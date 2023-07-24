from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

from .views import *


router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view({'get': 'download'})),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('users/subscriptions/', ManageSubscriptionsView.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', ManageSubscriptionsView.as_view({'post': 'create', 'delete': 'destroy'})),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]
