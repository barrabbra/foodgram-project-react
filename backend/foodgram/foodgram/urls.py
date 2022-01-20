from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('djoser.urls')),
    path('api/', include('recipes.urls')),
    path('admin/', admin.site.urls),
]
