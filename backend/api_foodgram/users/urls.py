from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf.urls import url

from .views import *


router = DefaultRouter()
router.register('', UsersViewSet, basename='users')

urlpatterns = [
    path('subscriptions/', ManageSubscriptionsView.as_view()),
    path('<int:id>/subscribe/', ManageSubscriptionsView.as_view()),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]
