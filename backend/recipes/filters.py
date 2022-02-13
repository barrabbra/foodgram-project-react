from django.db.models import IntegerField, Value
from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)

from .models import Favorite, Ingredient, Recipe, ShoppingCart


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'author',
        ]

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset
        if not Favorite.objects.filter(user=self.request.user).exists():
            return queryset
        recipes = self.request.user.favorites.recipes.all()
        return queryset.filter(
            pk__in=(recipes.values_list('id', flat=True,).get())
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        if not self.request.user.is_authenticated:
            return queryset
        if not ShoppingCart.objects.filter(user=self.request.user).exists():
            return queryset
        recipes = self.request.user.shopping_cart.recipes.all()
        return queryset.filter(
            pk__in=(recipes.values_list('id', flat=True).get())
        )


class IngredientSearchFilter(FilterSet):
    name = CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=(start_with_queryset.values_list('id', flat=True))
            ).annotate(order=Value(1, IntegerField()))
        )
        return start_with_queryset.union(contain_queryset).order_by('order')
