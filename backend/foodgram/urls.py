from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet
from django.urls import include, path


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
