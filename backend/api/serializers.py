import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from recipes.models import (Ingredient, Recipe, RecipeIngredients, Tag)
from users.models import MyUser


class Base64ImageField(serializers.ImageField):
    """Конвертация изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    """Теги."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
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
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class AbstractUserSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_avatar(self, obj):
        """Возвращаем аватар, если он есть, иначе возвращаем None."""
        return obj.avatar.url if obj.avatar else None


class RecipeSerializer(serializers.ModelSerializer):
    """Рецепты, основная модель."""

    ingredients = RecipeIngredientsSerializer(many=True, required=True)
    tags = TagsSerializer(many=True, read_only=True)
    author = AbstractUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags',
            'author', 'ingredients', 'image', 'text', 'name', 'cooking_time']

    def create(self, validated_data):
        """Метод для создания рецепта."""

        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        tags = Tag.objects.filter(id__in=self.initial_data.get('tags', []))
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['ingredient']['id']
                ),
                amount=ingredient_data['amount']
            )
        return recipe

    def to_representation(self, instance):
        """Метод для отображения всех полей ингредиентов."""

        representation = super().to_representation(instance)
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


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Избранные рецепты."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    avatar = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'recipes']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_avatar(self, obj):
        """Возвращаем аватар, если он есть, иначе возвращаем None."""
        return obj.avatar.url if obj.avatar else None
