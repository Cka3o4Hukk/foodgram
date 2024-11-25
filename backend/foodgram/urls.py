from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagsViewSet, IngredientViewSet
from django.urls import include, path


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/token/', include('djoser.urls.authtoken')),
  #  path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),

]
