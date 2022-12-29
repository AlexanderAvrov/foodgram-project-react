from collections import defaultdict

from recipes.models import IngredientRecipe


def download_ingredients(user):
    """Метод для формирования списка покупок"""
    ingredients = defaultdict(int)
    ingredient_recipes = IngredientRecipe.objects.filter(
        recipe__recipe_cart__user=user)

    for ingredient_recipe in ingredient_recipes:
        name = ingredient_recipe.ingredient.name
        measurement_unit = ingredient_recipe.ingredient.measurement_unit
        ingredient = f'{name}, {measurement_unit}'
        amount = ingredient_recipe.amount
        ingredients[ingredient] += amount

    ingredients_to_file = 'Список покупок:\n'
    count = 1

    for key, value in ingredients.items():
        ingredients_to_file += f'{count}. {key} - {value}\n'
        count += 1

    ingredients_to_file += '\n\n Foodgram ©'

    return ingredients_to_file
