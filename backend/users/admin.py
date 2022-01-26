from django.contrib.admin import ModelAdmin, register

from .models import Subscription, User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'date_joined',
        'last_login',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('role',)
    ordering = ('id',)
    empty_value_display = '-'
    readonly_fields = ('date_joined', 'last_login')


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = (
        'subscriber',
        'subscription',
    )
    search_fields = ('subscriber',)
    ordering = ('subscriber__id', )
    empty_value_display = '-'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
