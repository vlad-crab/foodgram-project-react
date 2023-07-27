from django.db.models import Sum

from api.models import ShoppingCart
from recipes.models import Ingredient, IngredientWithWT


def get_shopping_list(user):
    recipe_ids = []
    for obj in ShoppingCart.objects.filter(user=user):
        recipe_ids.append(obj.recipe.id)
    queryset = IngredientWithWT.objects.filter(
        recipe__in=recipe_ids
    ).values('ingredient_id').annotate(amount=Sum('amount'))
    shopping_cart = ''
    for item in queryset:
        ingredient = Ingredient.objects.get(pk=item['ingredient_id'])
        shopping_cart += (f'{ingredient.name} ({item["amount"]})'
                          f'{ingredient.measure_unit}, \n')
    return shopping_cart
