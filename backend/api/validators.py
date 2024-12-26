from rest_framework import serializers


'''def validate_empty_list(value):
    """Базовая проверка пустого списка"""

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")
    return value
'''


def validate_tags(value):
    """Проверка валидации тегов."""

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")

    if len(set(value)) != len(value):
        raise serializers.ValidationError("Не должно быть дубликатов.")
    return value


def validate_ingredients(value):
    """Проверка валидации ингредиентов."""

    if not value:
        raise serializers.ValidationError("Список не может быть пустым.")

    list_id = [i['ingredient']['id'] for i in value]

    if len(set(list_id)) != set(list_id):
        raise serializers.ValidationError("Не должно быть дубликатов.")

    return value
