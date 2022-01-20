from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from recipe.serializer import SubscribeRecipeSerializer

from .models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymouse:
            return False
        return user.id == obj


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name'
        ]


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = [
            'subscriber',
            'subscription',
        ]

    def validate_subscription(self, subscription):
        request = self.context['request']
        if request.user != subscription:
            return subscription
        raise serializers.ValidationError(
            _('Нельзя подписаться на себя')
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = SubscribeRecipeSerializer(Many=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymouse:
            return False
        return user.id == obj

    def get_recipes_count(self, obj):
        return obj.subscription.recipes.count()
