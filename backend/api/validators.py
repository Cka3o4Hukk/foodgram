from rest_framework import serializers
from recipes.models import Ingredient


def validate_empty_list(data, message):
    """Базовая проверка пустого списка"""

    if not data:
        raise serializers.ValidationError(message)


def validate_tags(data):
    """Проверка валидации тегов."""

    validate_empty_list(data, "Список тегов не может быть пустым")

    if len(set(data)) != len(data):
        raise serializers.ValidationError("Не должно быть дубликатов.")
    return data


def validate_ingredients(data):
    """Проверка валидации ингредиентов."""

    validate_empty_list(data, "Список ингредиентов не может быть пустым")

    list_id = [i['ingredient']['id'] for i in data]

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
    return data
