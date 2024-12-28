from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


def base_filter(self, queryset, name, value):
    user = self.request.user
    if user.is_authenticated:
        if value == 1:
            return queryset.filter(favorites__user=user)
        elif value == 0:
            return queryset.exclude(favorites__user=user)
    return queryset


class IsFavoritedFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        return base_filter(self, queryset, name, value)


class IsInShoppingCart(filters.FilterSet):
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart']

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return base_filter(self, queryset, name, value)


class RecipeFilter(IsFavoritedFilter, IsInShoppingCart):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
