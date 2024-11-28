from django.contrib.auth.models import AbstractUser
from django.db import models


class AbstractUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to='foodgram/users/images/',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
