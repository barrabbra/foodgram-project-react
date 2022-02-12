from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug',
        ]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'amount',
        ]
        extra_kwargs = {
            'id': {
                'read_only': False,
                'error_messages': {
                    'does_not_exist': 'Ингредиент не был найден',
                }
            },
            'amount': {
                'error_messages': {
                    'min_value': 'Минимальное  количество ингредиента 1'
                }
            }
        }


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        user = self.get_user()
        if not user.is_authenticated:
            return False
        if not Favorite.objects.filter(user=user).exists():
            return False
        return user.favorites.recipes.filter(pk__in=(obj.pk,)).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.get_user()
        if not user.is_authenticated:
            return False
        if not ShoppingCart.objects.filter(user=user).exists():
            return False
        return user.shopping_cart.recipes.filter(pk__in=(obj.pk,)).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateRecipeIngredientSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        )
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]
        extra_kwargs = {
            'cooking_time': {
                'error_messages': {
                    'min_value': 'Время приготовления не может быть меньше 1',
                }
            }
        }

    def validate(self, data):
        if data['cooking_time'] < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше 1 минуты'
            )
        if len(data['tags']) == 0:
            raise ValidationError('Выберите минимум один тег')
        if len(data['tags']) > len(set(data['tags'])):
            raise ValidationError('Каждый тег можно выбрать один раз')
        if len(data['ingredients']) == 0:
            raise ValidationError('Добавьте ингредиенты')
        id_ingredients = []
        for ingredient in data['ingredients']:
            if ingredient['amount'] == 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше нуля'
                )
            id_ingredients.append(ingredient['id'])
        if len(id_ingredients) > len(set(id_ingredients)):
            raise ValidationError('Ингредиенты не могут повторяться')
        return data

    def add_ingredients_and_tags(self, instance, validated_data):
        ingredients, tags = (
            validated_data.pop('ingredients'), validated_data.pop('tags')
        )
        for ingredient in ingredients:
            count_of_ingredient, _ = RecipeIngredient.objects.get_or_create(
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount'],
            )
            instance.ingredients.add(count_of_ingredient)
        for tag in tags:
            instance.tags.add(tag)
        return instance

    def create(self, validated_data):
        saved = {}
        saved['ingredients'] = validated_data.pop('ingredients')
        saved['tags'] = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(recipe, saved)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instance = self.add_ingredients_and_tags(instance, validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance, context=context).data
