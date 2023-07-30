from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientWithWT, Recipe,
                            ShoppingCart, Subscriptions, Tag)


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    fields = ('name', 'measure_unit')
    list_display = ('id', 'name', 'measure_unit')
    search_fields = ('name',)


class IngredientWithWTAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class TagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    verbose_name = 'tags'


class IngredientWithWTInLine(admin.TabularInline):
    model = Recipe.ingredients.through


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    exclude = ('ingredients', 'tags')
    inlines = (TagsInLine, IngredientWithWTInLine)
    search_fields = ('name',)
    list_filter = admin.ModelAdmin.list_filter + ('tags', 'author')
    list_display = admin.ModelAdmin.list_display + ('favorites_count',)

    def favorites_count(self, obj):
        return obj.users_favorites.all().count()


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('id', 'name', 'color', 'slug')


class ShoppingCartAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class SubscriptionsAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientWithWT, IngredientWithWTAdmin)
