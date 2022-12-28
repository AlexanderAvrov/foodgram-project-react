from django.db import models

from recipes.models import Recipe
from users.models import User


class ShoppingCart(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(
        User,
        verbose_name='Юзер',
        on_delete=models.CASCADE,
        related_name='user_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт для покупки',
        on_delete=models.CASCADE,
        related_name='recipe_cart',
    )

    class Meta:
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'

    def __str__(self):
        return f'{self.recipe} в корзине у {self.user}'
