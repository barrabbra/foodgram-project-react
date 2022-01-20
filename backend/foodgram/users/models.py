from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        USER = 'user', _('User')

    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    role = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['username']

    def __str__(self):
        return self.get_full_name()

    @property
    def is_admin(self):
        return self.role == self.UserType.ADMIN or self.is_staff


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    subscription = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список подписок'
        verbose_name_plural = 'Списки подписок'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscription'],
                name='Уникальная запись подписчик - автор',
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscription}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        related_name='cart',
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(
        'recipe.Recipe',
        verbose_name='Рецепты',
        related_name='in_shopping_carts',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Корзина {self.user}'
