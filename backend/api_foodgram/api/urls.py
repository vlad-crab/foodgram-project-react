from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingCartViewSet.as_view({'get': 'retrieve'})),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('users/subscriptions/', ManageSubscriptionsView.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', ManageSubscriptionsView.as_view({'post': 'create', 'delete': 'destroy'})),
    path('', include(router.urls)),
]
