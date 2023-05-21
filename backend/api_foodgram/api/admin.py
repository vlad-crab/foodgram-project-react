from django.contrib import admin
from .models import Ingredient, Recipe, Tag, ShoppingCart, Favorite


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
