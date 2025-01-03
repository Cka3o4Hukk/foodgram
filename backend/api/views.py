from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404  # , redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
#  from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response

from recipes.models import (Ingredient, FavoriteRecipe, Follow,
                            Recipe, ShoppingCart, Tag)
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    ShortRecipeSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)

User = get_user_model()

BASE_URL = '127.0.0.1'


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Создание рецепта, привязка автора."""
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        return context

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        return Response(
            {'short-link': f'{BASE_URL}/{pk}'},
            status=status.HTTP_200_OK
        )

    def shopping_cart_and_favorite(self, request, model, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        RECIPE_EXISTS = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if RECIPE_EXISTS:
                return Response(
                    {'detail': 'Вы уже добавили рецепт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.get_or_create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not RECIPE_EXISTS:
                return Response(
                    {'detail': 'Вы уже удалили рецепт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self.shopping_cart_and_favorite(request, FavoriteRecipe, pk)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self.shopping_cart_and_favorite(request, ShoppingCart, pk)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
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
    serializer_class = IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']


class TagViewSet(viewsets.ModelViewSet):
    """Теги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']  # для отладки убрать строчку


class UserViewSet(DjoserUserViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[IsAuthenticated])
    def get_me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Настройка подписки."""
        author = request.user
        current_user = self.get_object()
        SUBSCRIBE = Follow.objects.filter(
            author=author, subscriber=current_user)

        if current_user == author:
            return Response(
                {'detail': 'Подписка и отписка от самого себя невозможна'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if SUBSCRIBE.exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get_or_create(
                author=author,
                subscriber=current_user
            )
            user_serializer = FollowSerializer(
                author,
                context={'request': request},
            )
            recipes = author.recipes.all()
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit is not None:
                recipes = recipes[:int(recipes_limit)]

            recipe_serializer = ShortRecipeSerializer(recipes, many=True)
            response_data = {
                **user_serializer.data,
                'recipes': recipe_serializer.data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not SUBSCRIBE.exists():
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            SUBSCRIBE.delete()
            return Response(
                {'detail': 'Вы успешно отписались от пользователя'},
                status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Отображение подписок."""
        pass
        # if not request.user.is_authenticated:
        #     return Response(
        #         {'detail': 'Пользователь не аутентифицирован'},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )

        # subscriptions = Follow.objects.filter(
        #     user=request.user).select_related('following')
        # subscribed_users = [follow.following for follow in subscriptions]
        # paginator = LimitOffsetPagination()
        # paginated_users = paginator.paginate_queryset(subscribed_users,
        #                                               request)

        # serializer = FollowSerializer(paginated_users, many=True)
        # return paginator.get_paginated_response(serializer.data)
