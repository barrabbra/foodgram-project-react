from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
import rest_framework

from .models import Tag, Ingredient, RecipeIngredient, Recipe
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
