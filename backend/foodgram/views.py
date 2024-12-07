from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Ingredient, FavoriteRecipe, Recipe, Tag  # Follow
from .serializers import (
    IngredientsSerializer, FavoriteRecipeSerializer,
    RecipeSerializer, TagsSerializer)
# AbstractUserSerializer, FollowSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Создание рецепта, привязка автора."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe
                                             ).exists():
                return Response(
                    {'detail': 'Вы уже добавили этот рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            # Удаление рецепта из избранного
            favorite_recipe = get_object_or_404(
                FavoriteRecipe,
                user=user,
                recipe=recipe
            )
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class TagViewSet(viewsets.ModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


'''class SubscribeViewSet(viewsets.ModelViewSet):
    """Подписки."""
    pass    @serializer_class = FollowSerializer
    permission_classes = [AllowAny  ]
    queryset = Follow.objects.all()

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        user_to_subscribe = self.get_object()
        if request.method == 'POST':
            # Logic to create a subscription
            Follow.objects.get_or_create(user=request.user,
            followed_user=user_to_subscribe)
            return Response({'status': 'subscribed'})
        elif request.method == 'DELETE':
            # Logic to delete a subscription
            Follow.objects.filter(user=request.user,
            followed_user=user_to_subscribe).delete()
            return Response({'status': 'unsubscribed'})


    subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(AbstractUser, id=pk)

        if not user.follower.filter(author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)'''
