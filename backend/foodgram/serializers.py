from rest_framework import serializers
from .models import Ingredient, Recipe, Tag, RecipeIngredients



'''from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user'''
    

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientsSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['name', 'text', 'cooking_time', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')  # Извлекаем данные ингредиентов
        recipe = Recipe.objects.create(**validated_data)  # Создаем рецепт
        print("Словарик:", ingredients_data)

        for ingredient_data in ingredients_data:
            print("Часть словаря: ", ingredient_data)
            amount = ingredient_data['amount'] # amount = 5
            print("Amount", amount)
            id = ingredient_data['ingredient']['id'] # ingredient = {id:1}
            print("id", id)
            RecipeIngredients.objects.create(recipe=recipe, ingredient=Ingredient.objects.get(id=id), amount=amount)
        return recipe
