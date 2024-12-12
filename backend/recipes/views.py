from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredient, FavoriteRecipe, Recipe, Tag
from api.serializers import (
    IngredientsSerializer,
    FavoriteRecipeSerializer,
    RecipeSerializer,
    TagsSerializer
)
from http import HTTPStatus

# AbstractUserSerializer, FollowSerializer

HTTP_BAD_REQUEST = HTTPStatus.BAD_REQUEST


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Создание рецепта, привязка автора."""

        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        FAVORITE_RECIPE_EXISTS = FavoriteRecipe.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if FAVORITE_RECIPE_EXISTS:
                return Response(
                    {'detail': 'Вы уже добавили этот рецепт в избранное.'},
                    status=HTTP_BAD_REQUEST
                )
            FavoriteRecipe.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not FAVORITE_RECIPE_EXISTS:
                return Response(
                    {'detail': 'Вы уже удалили рецепт из избранного.'},
                    status=HTTP_BAD_REQUEST
                )
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class TagViewSet(viewsets.ModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
