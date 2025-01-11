import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer)
from djoser.serializers import UserSerializer as DjoserUserSerializer

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag, Follow
from .validators import validate_ingredients, validate_tags

User = get_user_model()

MIN_VALUE = 1
MAX_VALUE = 32000


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'password']


class UserSerializer(DjoserUserSerializer):
    """Отображение пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Follow.objects.filter(author=author, subscriber=user).exists()


class Base64ImageField(serializers.ImageField):
    """Конвертация изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    """Аватар пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']


class TagSerializer(serializers.ModelSerializer):
    """Теги."""

    def validate_tag_exists(value):
        if not Tag.objects.filter(id=value).exists():
            raise serializers.ValidationError("Тег с указанным ID не найден.")
        return value

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для всех полей ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Рецепты, промежуточная модель."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепты, основная модель."""

    ingredients = RecipeIngredientsSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'image',
                  'text', 'name', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart']

    def get_is_favorited(self, recipe):
        user = self.context['request'].user  # user.id для анонима = None
        return recipe.favorites.filter(user=user.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return recipe.shopping_cart.filter(user=user.id).exists()

    def validate_tags(self, data):
        """Проверка списка тегов."""

        return validate_tags(data)

    def validate_ingredients(self, data):
        """Проверка списка ингредиентов."""

        return validate_ingredients(data)

    def fill_with_ingredients(self, recipe, ingredients_data):
        """Метод наполнения рецепта."""

        RecipeIngredients.objects.bulk_create(
            RecipeIngredients(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['ingredient']['id']
                ),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data)

        return recipe

    def create(self, validated_data):
        """Метод для создания рецепта."""

        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        return self.fill_with_ingredients(recipe, ingredients_data)

    def update(self, recipe, validated_data):
        """Метод для обновления рецепта."""

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                {"ingredients": "Не передан список ингредиентов."}
            )

        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                {"tags": "Не передан список тегов."}
            )

        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe.save()

        # Обновляем теги, если они были переданы
        if tags_data is not None:
            recipe.tags.set(tags_data)

        # Обновляем ингредиенты
        if ingredients_data is not None:
            # Удаляем старые ингредиенты
            recipe.ingredients.all().delete()

        return self.fill_with_ingredients(recipe, ingredients_data)

    def to_representation(self, instance):
        """Метод для отображения всех полей ингредиентов."""

        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        representation['ingredients'] = [
            {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': recipe_ingredient.
                ingredient.measurement_unit,
                'amount': recipe_ingredient.amount
            }
            for recipe_ingredient in instance.ingredients.all()
        ]
        return representation


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'avatar', 'recipes_count']

    def validate_subscription(self):
        """Проверка подписки на самого себя."""
        request = self.context.get('request')

        if request.user == self.instance:
            raise serializers.ValidationError(
                {'detail': 'Подписка и отписка от самого себя невозможна'}
            )
        if Follow.objects.filter(author=self.instance,
                                 subscriber=request.user).exists():
            raise serializers.ValidationError(
                {'detail': 'Вы уже подписаны на этого пользователя'}
            )

    def to_representation(self, instance):
        """Преобразует объект в словарь с учетом лимита рецептов."""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            representation['recipes'] = representation[
                'recipes'][:int(recipes_limit)]
        return representation
