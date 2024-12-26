from rest_framework import serializers
from recipes.models import Ingredient


def validate_empty_list(value, message):
    """Базовая проверка пустого списка"""

    if not value:
        raise serializers.ValidationError(message)


def validate_tags(value):
    """Проверка валидации тегов."""

    validate_empty_list(value, "Список тегов не может быть пустым")

    if len(set(value)) != len(value):
        raise serializers.ValidationError("Не должно быть дубликатов.")
    return value


def validate_ingredients(value):
    """Проверка валидации ингредиентов."""

    validate_empty_list(value, "Список ингредиентов не может быть пустым")

    list_id = [i['ingredient']['id'] for i in value]

    existing_ingredients = Ingredient.objects.filter(
        id__in=list_id).values_list('id', flat=True)
    missing_ingredients = set(list_id) - set(existing_ingredients)

    if missing_ingredients:
        raise serializers.ValidationError(
            f"Ингредиенты с ID {', '.join(map(str, missing_ingredients))} "
            "не найдены в базе данных."
        )

    if len(set(list_id)) != len(list_id):
        raise serializers.ValidationError("Не должно быть дубликатов.")
    return value
