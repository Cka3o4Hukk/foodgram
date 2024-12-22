from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Ingredient, FavoriteRecipe, Follow, Recipe, Tag
from .serializers import (
    AbstractUserSerializer,
    AvatarSerializer,
    FavoriteRecipeSerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    TagsSerializer
)
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Создание рецепта, привязка автора."""

        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    def retrieve(self, request, pk=None):
        """Создание короткой ссылки."""

        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        short_link = f'http://127.0.0.1:8000/api/r/{recipe.id}'
        response_data = {
            'recipe': serializer.data,
            'short_link': short_link
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def short_link_redirect(self, request, recipe_id):
        """Преобразование короткой ссылки в действующую."""
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            return redirect(f'http://127.0.0.1:8000/api/recipes/{recipe.id}/')
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    def shopping_cart_and_favorite(self, request, pk=None):
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
                    {'detail': 'Вы уже добавили рецепт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.get_or_create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not FAVORITE_RECIPE_EXISTS:
                return Response(
                    {'detail': 'Вы уже удалили рецепт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        return self.shopping_cart_and_favorite(request, pk)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        return self.shopping_cart_and_favorite(request, pk)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_recipe(self, request):
        recipes = self.queryset
        ingredient_totals = {}

        for rec in recipes:
            for recipe_ingredient in rec.ingredients.all():
                ingredient_name = recipe_ingredient.ingredient.name
                amount = recipe_ingredient.amount
                measurement_unit = (recipe_ingredient.ingredient
                                    .measurement_unit)

                if ingredient_name in ingredient_totals:
                    ingredient_totals[ingredient_name]['amount'] += amount
                else:
                    ingredient_totals[ingredient_name] = {
                        'amount': amount,
                        'unit': measurement_unit
                    }

        recipe_text = "Список ингредиентов:\n"
        for ingredient_name, data in ingredient_totals.items():
            recipe_text += (
                f"• {ingredient_name}: "
                f"{data['amount']}{data['unit']}\n"
            )

        response = HttpResponse(recipe_text, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response


class IngredientViewSet(viewsets.ModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    #  http_method_names = ['get']


class TagViewSet(viewsets.ModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    #  http_method_names = ['get']  #для отладки убрать строчку


class UserViewSet(DjoserUserViewSet):
    serializer_class = AbstractUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()

    #  def list(self, request, *args, **kwargs):
    #    """Метод для всех GET-запросов, выводит список пользователей."""

    #    queryset = User.objects.all()
    #    serializer = self.get_serializer(queryset, many=True)
    #    return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def update_avatar(self, request):
        """Добавление аватара текущего пользователя."""

        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        """Настройка подписки."""

        SUBSCRIBE = Follow.objects.filter(
            user=request.user,
            following=self.get_object()
        )

        if request.user == self.get_object():
            return Response(
                {'error': 'Подписка и отписка от самого себя невозможнаа'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if SUBSCRIBE.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get_or_create(
                user=request.user,
                following=self.get_object()
            )
            return Response(
                {'status': 'Вы успешно подписались на пользователя'})

        elif request.method == 'DELETE':
            if not SUBSCRIBE.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            SUBSCRIBE.delete()
            return Response(
                {'status': 'Вы успешно отписались от пользователя'})

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Отображение подписок."""

        if not request.user.is_authenticated:
            return Response(
                {'error': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        subscriptions = Follow.objects.filter(
            user=request.user).select_related('following')
        subscribed_users = [follow.following for follow in subscriptions]

        serializer = FollowSerializer(subscribed_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
