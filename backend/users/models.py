from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(
        verbose_name='Емейл', unique=True, max_length=254)
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150)
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)
    password = models.CharField(verbose_name='Пароль', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
