from rest_framework.routers import DefaultRouter
from recipes.views import (
    RecipeViewSet, TagViewSet, IngredientViewSet)
from django.urls import include, path
from users.views import UserViewSet


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('r/<int:recipe_id>/', RecipeViewSet.as_view(
        {'get': 'short_link_redirect'}), name='short-link-redirect'),
]
