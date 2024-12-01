from rest_framework import serializers

from users.models import MyUser


from django.contrib.auth.hashers import make_password


class AbstractUserSerializer(serializers.ModelSerializer):
    """Кастомный пользователь."""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar', 'password']  # Добавлено поле password
        extra_kwargs = {
            'password': {'required': True},
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_avatar(self, obj):
        """Возвращаем аватар, если он есть, иначе возвращаем None."""
        return obj.avatar.url if obj.avatar else None

    def create(self, validated_data):
        """Создаем пользователя с хешированным паролем."""
        password = validated_data.pop('password')
        user = MyUser(**validated_data)
        user.password = make_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """Не выводим пароль после удачного запроса."""
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation
