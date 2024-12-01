from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import AbstractUser
# from .permissions import AllowPostWithoutToken
from foodgram.serializers import AbstractUserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet
from foodgram.serializers import AvatarSerializer
from foodgram.models import Follow


class UserViewSet(DjoserUserViewSet):
    serializer_class = AbstractUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = AbstractUser.objects.all()

    @action(detail=False, methods=['put'], url_path='me/avatar',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def update_avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user_to_subscribe = self.get_object()  # Assuming you want to subscribe to a user identified by pk
        if request.method == 'POST':
        # Логика для создания подписки
            Follow.objects.get_or_create(user=request.user, following=user_to_subscribe)  # Измените на following
            return Response({'status': 'subscribed'})
        elif request.method == 'DELETE':
            # Логика для удаления подписки
            Follow.objects.filter(user=request.user, following=user_to_subscribe).delete()  # Измените на following
            return Response({'status': 'unsubscribed'})
