from rest_framework import serializers

from users.models import AbstractUser


class AbstractUserSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = AbstractUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_avatar(self, obj):
        """Возвращаем аватар, если он есть, иначе возвращаем None."""
        return obj.avatar.url if obj.avatar else None
