import base64

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from rest_framework import serializers

from .validators import validate_ingredients, validate_tags
from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag
from users.models import User


MIN_VALUE = 1
MAX_VALUE = 32000


class AbstractUserSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'avatar', 'is_subscribed', 'password']
        extra_kwargs = {
            'password': {'required': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_avatar(self, obj):
        """Возвращаем аватар, если он есть, иначе возвращаем None."""
        return obj.avatar.url if obj.avatar else None

    def create(self, validated_data):
        """Создаем пользователя с хешированным паролем."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = make_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """Не выводим пароль после удачного запроса."""
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation


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
    author = AbstractUserSerializer(read_only=True)
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

    def validate_tags(self, value):
        """Проверка на пустой список тегов."""
        return validate_tags(value)

    def validate_ingredients(self, value):
        """Проверка на пустой список ингредиентов."""
        return validate_ingredients(value)

    def create(self, validated_data):
        """Метод для создания рецепта."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['ingredient']['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]

        RecipeIngredients.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""

        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = self.initial_data.get('tags', [])

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.save()

        tags = Tag.objects.filter(id__in=tags_data)
        instance.tags.set(tags)

        if ingredients_data is not None:
            instance.ingredients.all().delete()

            recipe_ingredients = [
                RecipeIngredients(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(
                        id=ingredient_data['ingredient']['id']),
                    amount=ingredient_data['amount']
                )
                for ingredient_data in ingredients_data
            ]
            RecipeIngredients.objects.bulk_create(recipe_ingredients)

        return instance

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
        model = User
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
