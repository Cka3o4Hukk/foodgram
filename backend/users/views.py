
from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers import FollowSerializer
from recipes.models import Follow
from .serializers import AbstractUserSerializer, AvatarSerializer
from .models import MyUser

User = get_user_model()

HTTP_400 = status.HTTP_400_BAD_REQUEST


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
        """Настройка подписки."""

        SUBSCRIBE = Follow.objects.filter(
            user=request.user,
            following=self.get_object()
        )

        if request.user == self.get_object():
            return Response(
                {'error': 'Подписка и отписка от самого себя невозможнаа'},
                status=HTTP_400
            )
        if request.method == 'POST':
            if SUBSCRIBE.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=HTTP_400
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
                    status=HTTP_400
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
