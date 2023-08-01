from django.db.models import Case, Q, Value, When
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
    )
    author = filters.NumberFilter(
        method='get_is_author'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'is_in_shopping_cart', 'is_favorited', 'author')

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(users_carts__user=self.request.user)
        return queryset

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(users_favorites__user=self.request.user)
        return queryset

    def get_is_author(self, queryset, name, value):
        if value:
            return queryset.filter(author_id=value)
        return queryset


class TagFilter(FilterSet):
    name = filters.CharFilter(
        method='get_ordered_and_filtered_queryset'
    )

    class Meta:
        model = Tag
        fields = ('name', )

    def get_ordered_and_filtered_queryset(self, queryset, name, value):
        if value:
            queryset = queryset.filter(name_icontains=value)
            queryset = queryset.annotate(
                filter_flag=Case(
                    When(Q(name__istartswith=value), then=Value(1)),
                    default=Value(0)
                )
            ).order_by('-filter_flag')
        return queryset
