from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag, User


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов"""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр для рецептов"""

    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Метод для фильтрации избранных рецептов"""
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(recipe_in_favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Метод для фильтрации рецептов в корзине"""
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(recipe_cart__user=self.request.user)
        return queryset
