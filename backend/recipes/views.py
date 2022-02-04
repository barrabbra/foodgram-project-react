import os

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from foodgram.paginations import LimitPageSizePagination
from users.permissions import IsAdminOrAuthorOrReadOnly
from users.serializers import LiteRecipeSerializer
from .filters import IngredientSearchFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .pdfrender import render_pdf_view
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageSizePagination
    permission_classes = (IsAdminOrAuthorOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )

    def add_to_favorite(self, request, recipe):
        try:
            Favorite.objects.create(user=request.user, favorite=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Вы уже подписаны на данного автора'},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = LiteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from_favorite(self, request, recipe):
        favorite = Favorite.objects.filter(user=request.user, favorite=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Данный автор не найден в подписках'},
                status=HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.add_to_favorite(request, recipe)
        return self.delete_from_favorite(request, recipe)

    def generate_shopping_ingredients(self, request, shopping_cart):
        return (
            shopping_cart.order_by('recipes__ingredients__ingredient__name')
            .values('recipes__ingredients__ingredient__name',
                    'recipes__ingredients__ingredient__measurement_unit')
            .annotate(total=Sum('recipes__ingredients__amount'))
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        try:
            shopping_cart = ShoppingCart.objects.get(user=request.user)
        except ShoppingCart.DoesNotExist:
            return Response(
                {'errors': 'Данные о корзине не найдены'},
                status=HTTP_400_BAD_REQUEST
            )
        context = {
            'context': self.generate_shopping_ingredients(request,
                                                          shopping_cart)
        }
        template_path = os.path.join(settings.TEMPLATES_DIR,
                                     'recipes/shopping_cart.html')
        return render_pdf_view(request, context, template_path)

    def add_to_shopping_cart(self, request, recipe, shopping_cart):
        if shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': 'Вы уже добавили данный рецепт в корзину'},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.add(recipe)
        serializer = LiteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from_shopping_cart(self, request, recipe, shopping_cart):
        if not shopping_cart.recipes.filter(pk__in=(recipe.pk,)).exists():
            return Response(
                {'errors': 'Рецепт не был найдет в корзине'},
                status=HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipes.remove(recipe)
        return Response(
            status=HTTP_204_NO_CONTENT,
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart = (
            ShoppingCart.objects.get_or_create(user=request.user)[0]
        )
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe, shopping_cart)
        return self.delete_from_shopping_cart(request, recipe, shopping_cart)
