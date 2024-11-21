from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator, RegexValidator)


User = get_user_model()


class Tags(models.Model):
    slug_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_-]+$',
        message='Slug должен содержать только буквы, цифры и дефисы.'
    )

    name = models.CharField(
        max_length=32,
        unique=True,
    )
    slug = models.SlugField(
        max_length=32,
        unique=True,
        validators=[slug_validator]
    )

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=64,
        unique=True
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes'
    )
    # image = models.CharField(string)
    name = models.CharField(
        max_length=256,
        unique=True
    )
    text = models.CharField(
        max_length=256
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.name


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

# мб мэни мэни

# class Recipe
# избранное и список покупок - manytomany
# короткая ссылка - можно поискать батарейку в инете как это сделать
# создать рецепт - только зареганные
