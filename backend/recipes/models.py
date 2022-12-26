from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from foodgram.constants import MIN_TIME, MESSAGE_ERR_TIME


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(verbose_name='Ингредиент', max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тегов"""

    name = models.CharField(verbose_name='Тег', max_length=200)
    color = models.CharField(verbose_name='Цвет HEX-code', max_length=7)
    slug = models.SlugField(verbose_name='Адрес', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(verbose_name='Название рецепта', max_length=200)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        help_text='Загрузите изображение',
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_TIME, message=MESSAGE_ERR_TIME)]
    )
    tags = models.ManyToManyField(Tag, through='TagRecipe')

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингредиентов определённого рецепта"""

    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт ингредиента',
        related_name='recipe_from_ingredient', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиент в рецепте',
        related_name='ingredient_for_recipe', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество', blank=False, max_length=64)

    class Meta:
        verbose_name = 'Ingredient for recipe'
        verbose_name_plural = 'Ingredients for recipe'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class TagRecipe(models.Model):
    """Модель тегов определённого рецепта"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Tag for recipe'
        verbose_name_plural = 'Tags for recipe'

    def __str__(self):
        return f'{self.recipe} - {self.tag}'


class Favorite(models.Model):
    """Модель избранного рецепта"""

    user = models.ForeignKey(
        User,
        verbose_name='Юзер добавивший в избранное',
        on_delete=models.CASCADE,
        related_name='is_favorited',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_in_favorite',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite',
        )]
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipe'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class Subscription(models.Model):
    """Модель подписки"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписавшийся',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписан на:',
        on_delete=models.CASCADE,
        related_name='author_recipes',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow',
        )]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} - {self.author}'
