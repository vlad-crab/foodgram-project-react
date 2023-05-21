from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url

from .views import *


router = DefaultRouter()
router.register('', UsersViewSet, basename='users')

urlpatterns = [
    path('subscriptions/', ManageSubscriptionsView.as_view({"get": "list"})),
    path('<int:id>/subscribe/', ManageSubscriptionsView.as_view({"post": "create", "delete": "destroy"})),
]
