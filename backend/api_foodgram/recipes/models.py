from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    name = models.TextField()
    measure_unit = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class IngredientWithWT(models.Model):
    amount = models.IntegerField(
        blank=False,
        null=False,
        default=1,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='weights'
    )

    class Meta:
        verbose_name = 'Ингредиент с количеством'
        verbose_name_plural = 'Ингредиенты с количеством'

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount} '
                f'{self.ingredient.measure_unit}')


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
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'