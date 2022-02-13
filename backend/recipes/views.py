# import os
#
# from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from foodgram.paginations import LimitPageSizePagination
from recipes.constants import (FAVORITE_ADD_ERROR, FAVORITE_DELETE_ERROR,
                               SHOPPING_CART_ADD_ERROR,
                               SHOPPING_CART_DELETE_ERROR,
                               SHOPPING_CART_GET_ERROR)
from recipes.filters import IngredientSearchFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
# from recipes.pdfrender import render_pdf_view
from recipes.serializers import (CreateRecipeSerializer, IngredientSerializer,
                                 RecipeSerializer, TagSerializer)
from users.permissions import IsAdminOrAuthorOrReadOnly
from users.serializers import LiteRecipeSerializer


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

    def add_to(self, request, pk, model, error):
        model_object = model.objects.get_or_create(user=request.user)[0]
        if model_object.recipes.filter(pk__in=pk).exists():
            return Response(
                {'errors': error},
                status=HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        model_object.recipes.add(recipe)
        serializer = LiteRecipeSerializer(recipe)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
        )

    def delete_from(self, request, pk, model, error):
        try:
            model_object = model.objects.get(user=request.user)
        except model.DoesNotExist:
            return Response(
                {'errors': error},
                status=HTTP_400_BAD_REQUEST,
            )
        if not model_object.recipes.filter(pk__in=pk).exists():
            return Response(
                {'errors': error},
                status=HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        model_object.recipes.remove(recipe)
        return Response(
            status=HTTP_204_NO_CONTENT,
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to(
                request=request,
                pk=pk,
                model=Favorite,
                error=FAVORITE_ADD_ERROR,
            )
        return self.delete_from(
            request=request,
            pk=pk,
            model=Favorite,
            error=FAVORITE_DELETE_ERROR,
        )

    def generate_shopping_ingredients(self, request, shopping_cart):
        return (
            shopping_cart.order_by('recipes__ingredients__ingredient__name')
            .values('recipes__ingredients__ingredient__name',
                    'recipes__ingredients__ingredient__measurement_unit')
            .annotate(total=Sum('recipes__ingredients__amount'))
        )

    @action(detail=False)
    def download_shopping_cart(self, request):
        if not ShoppingCart.objects.filter(user=request.user).exists():
            return Response(
                {'errors': SHOPPING_CART_GET_ERROR},
                status=HTTP_400_BAD_REQUEST
            )
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        context = {
            'context': self.generate_shopping_ingredients(request,
                                                          shopping_cart)
        }
        # template_path = os.path.join(settings.TEMPLATES_DIR,
        #                              'recipes/shopping_cart.html')
        # return render_pdf_view(request, context, template_path)

        response = HttpResponse(context, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment;' 'filename="shopping_cart.txt"'
        )
        return response

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_to(
                request=request,
                pk=pk,
                model=ShoppingCart,
                error=SHOPPING_CART_ADD_ERROR,
            )
        return self.delete_from(
            request=request,
            pk=pk,
            model=ShoppingCart,
            error=SHOPPING_CART_DELETE_ERROR,
        )
