from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
