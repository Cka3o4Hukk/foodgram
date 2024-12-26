from rest_framework import serializers

def validate_empty_list(value):
    """Базовая проверка пустого списка"""

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")
    return value


def validate_tags(value):
    """Проверка на пустой список тегов."""
    print(value, 'tags')

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")
    return value


def validate_ingredients(value):
    """Проверка на пустой список ингредиентов."""
    print(value, 'ingr')

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")
    return value
