from rest_framework import serializers
from .models import Ingredient, Recipe, Tag, RecipeIngredients
from users.models import AbstractUser
import base64
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class AbstractUserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = AbstractUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']


class RecipeSerializer(serializers.ModelSerializer):
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
        print(validated_data)
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


'''class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователей"""
    author = AbstractUserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = '__all__' '''


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
