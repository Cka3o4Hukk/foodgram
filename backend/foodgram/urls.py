from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagsViewSet, IngredientViewSet, UserSubscriptionsViewSet
from django.urls import include, path


router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagsViewSet)
router.register(r'users', UserSubscriptionsViewSet, basename='user-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    #  path('users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
]
