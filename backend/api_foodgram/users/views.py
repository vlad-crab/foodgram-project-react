from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.response import Response

from .models import Subscriptions
from .permissions import IsAuthenticated
from .serializers import UsersSerializer, UsersWithRecipesSerializer


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination
    queryset = User.objects.all()


class ManageSubscriptionsView(viewsets.ModelViewSet):
    serializer_class = UsersWithRecipesSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = self.request.user
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

    def perform_destroy(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        user = self.request.user
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
