from django.contrib import admin

from .models import (Recipe, Tag, Ingredient, IngredientRecipe, TagRecipe,
                     Subscription, Favorite)

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Subscription)
admin.site.register(Favorite)
