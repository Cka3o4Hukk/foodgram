from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator, RegexValidator)


User = get_user_model()


class Tag(models.Model):
    slug_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_-]+$',
        message='Slug должен содержать только буквы, цифры и дефисы.'
    )
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        validators=[slug_validator],
        verbose_name='Тег'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )
    image = models.ImageField(
        upload_to='foodgram/recipes/images/',
        verbose_name='Изображение'
    )
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название'
    )
    text = models.CharField(
        max_length=256,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин)'
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')


class ShoppingCart(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True
    )
    # image = ссылка на картинку на сайте
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Автор рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_constraint'
            )
        ]
