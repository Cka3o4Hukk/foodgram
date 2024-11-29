from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Recipe, Ingredient, Tag, FavoriteRecipe
from .serializers import (AbstractUserSerializer, FavoriteRecipeSerializer,
    RecipeSerializer, IngredientsSerializer, TagsSerializer)
from users.models import AbstractUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djoser.serializers import UserSerializer
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            # Проверка, если рецепт уже в избранном
            if FavoriteRecipe.objects.filter(user=user, recipe=recipe
                                             ).exists():
                return Response(
                    {'detail': 'Вы уже добавили этот рецепт в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Добавление рецепта в избранное
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
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class UserSubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=('POST',))
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(AbstractUser, id=pk)
        serializer = UserSubscriptionSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    '''@subscribe.mapping.delete
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
