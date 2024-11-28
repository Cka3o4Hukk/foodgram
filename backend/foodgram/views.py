from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Recipe, Ingredient, Tag
from .serializers import (AbstractUserSerializer, UserSubscriptionSerializer,
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


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class UserSubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=('POST',))
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(AbstractUser, id=id)
        serializer = UserSubscriptionSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        user = request.user
        author = get_object_or_404(AbstractUser, id=id)

        if not user.follower.filter(author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = get_object_or_404(Follow, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
