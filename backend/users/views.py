# from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly  # , #AllowAny

# from .permissions import AllowPostWithoutToken
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from django.contrib.auth import get_user_model
# from rest_framework.response import Response


from api.serializers import RecipeSerializer
from recipes.models import Follow, Recipe
from .serializers import AbstractUserSerializer, AvatarSerializer
from .models import MyUser


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    serializer_class = AbstractUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = MyUser.objects.all()

    def list(self, request, *args, **kwargs):
        """Метод для всех GET-запросов, выводит список пользователей."""
        queryset = MyUser.objects.all()
        serializer = self.get_serializer(queryset, many=True)
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

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user_to_subscribe = self.get_object()
        if request.method == 'POST':
            Follow.objects.get_or_create(
                user=request.user,
                following=user_to_subscribe
            )
            serializer = AbstractUserSerializer(user_to_subscribe)
            recipes = Recipe.objects.filter(author=user_to_subscribe)
            recipes_serializer = RecipeSerializer(recipes, many=True)

            return Response({
                'user': serializer.data,
                'recipes': recipes_serializer.data
            }, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            Follow.objects.filter(
                user=request.user,
                following=user_to_subscribe
            ).delete()
            return Response({'status': 'unsubscribed'})
