from django.contrib.admin import ModelAdmin, display, register

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color',)
    search_fields = ('name', 'slug',)
    ordering = ('color',)
    empty_value_display = '-'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('measurement_unit',)
    empty_value_display = '-'


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author',)
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('added_in_favorites',)
    empty_value_display = '-'

    @display(description='Общее число добавлений в избранное')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@register(RecipeIngredient)
class CountOfIngredientAdmin(ModelAdmin):
    list_display = (
        'id', 'ingredient', 'amount', 'get_measurement_unit',
        'get_recipes_count',
    )
    readonly_fields = ('get_measurement_unit',)
    list_filter = ('ingredient',)
    ordering = ('ingredient',)
    empty_value_display = '-'

    @display(description='Единица измерения')
    def get_measurement_unit(self, obj):
        try:
            return obj.ingredient.measurement_unit
        except RecipeIngredient.ingredient.RelatedObjectDoesNotExist:
            return '-'

    @display(description='Количество ссылок в рецептах')
    def get_recipes_count(self, obj):
        return obj.recipes.count()


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user',)
    list_filter = ('user', 'recipes',)
    empty_value_display = '-'


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', )
    list_filter = ('user', 'recipes')
    empty_value_display = '-'
