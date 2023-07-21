from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField()
    measure_unit = models.TextField()

    def __str__(self):
        return self.name


class IngredientWithWT(models.Model):
    amount = models.IntegerField(blank=False)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='weights'
    )

    def __str__(self):
        return f'{self.ingredient.name} {self.amount} {self.ingredient.measure_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        null=False
    )
    name = models.TextField(verbose_name='Название')
    image = models.ImageField(
        upload_to='images/',
        blank=True,
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        IngredientWithWT,
        blank=False,
        related_name='recipe'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering  = ['-pub_date',]

    def __str__(self):
        return f'{self.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_carts'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_constraint'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_favorites'
    )


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_constraint'
            )
        ]
