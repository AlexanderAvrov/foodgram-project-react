from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     Subscription, Tag, TagRecipe)


class IngredientRecipeAdminInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 3


class TagRecipeAdminInLine(admin.TabularInline):
    model = TagRecipe
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Рецептов"""

    list_display = ('id', 'name', 'author', 'cooking_time', 'pub_date')
    search_fields = ('name',)
    list_filter = ('tags', 'name', 'author')
    inlines = (IngredientRecipeAdminInLine, TagRecipeAdminInLine)

    fieldsets = (
        ('Основные данные', {
            'fields': ('name', 'author', 'image', 'pub_date')
        }),
        ('Приготовление', {
            'fields': ('text', 'cooking_time')
        }),
        ('Счётчики', {
            'fields': ('in_favorite_count', 'in_cart_count')
        })
    )
    readonly_fields = ('in_favorite_count', 'in_cart_count', 'pub_date')

    def in_favorite_count(self, obj):
        return obj.recipe_in_favorite.count()

    def in_cart_count(self, obj):
        return obj.recipe_cart.count()

    in_favorite_count.short_description = 'Пользователей, добавили в избранное:'
    in_cart_count.short_description = 'Пользователей, добавили в корзину:'


class IngredientsAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Ингредиентов"""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Ингредиенты-Рецепт"""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Subscription)
admin.site.register(Favorite)
