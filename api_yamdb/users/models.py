from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class UserRoles(models.TextChoices):
    USER = 'user', 'Пользователь'
    MODERATOR = 'moderator', 'Модератор'
    ADMIN = 'admin', 'Администратор'


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True,)
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='фамилия пользователя'
    )
    bio = models.TextField(
        max_length=999,
        verbose_name='биография',
        blank=True,
    )
    role = models.CharField(
        max_length=100,
        verbose_name='роль пользователя',
        choices=UserRoles.choices,
        default='user',
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=150,
        blank=True
    )

    class Meta:
        ordering = ('username',)

    def get_token(self):
        refresh = RefreshToken.for_user(User)
        return str(refresh.access_token)

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == UserRoles.USER

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == UserRoles.ADMIN
            or self.is_superuser
            or self.is_staff
        )
