from rest_framework.routers import DefaultRouter
from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet)
from django.urls import include, path
from users.views import UserViewSet


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
