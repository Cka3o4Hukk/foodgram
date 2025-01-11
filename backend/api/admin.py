from django.contrib import admin

from recipes.models import FavoriteRecipe, Ingredient, Recipe, Tag
from users.models import User


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    list_filter = ('id', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'author', 'name', 'text',
                    'cooking_time', 'image')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    search_fields = ('user', )
    list_display = ('id', 'user', 'recipe')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', )
    list_display = ('email', 'first_name', 'last_name')
