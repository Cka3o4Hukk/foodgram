from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import AbstractUser
# from .permissions import AllowPostWithoutToken
from foodgram.serializers import AbstractUserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet


class UserViewSet(DjoserUserViewSet):
    serializer_class = AbstractUserSerializer
    permission_classes = [AllowAny]
    queryset = AbstractUser.objects.all()
