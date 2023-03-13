from datetime import datetime, timedelta

import pytest

from users.tasks import email

try:
    from users.models import User
except ImportError:
    assert False, 'Не найдена модель User'

try:
    from recipes.models import Subscription
except ImportError:
    assert False, 'Не найдена модель Subscription'

try:
    from recipes.models import Recipe
except ImportError:
    assert False, 'Не найдена модель Recipe'


@pytest.fixture
def user_1(db):
    user_1 = User.objects.create(
        email='test_1@mail.ru', username='test_1', password='12345')
    return user_1


@pytest.fixture
def user_2(db):
    user_2 = User.objects.create(
        email='test_2@mail.ru', username='test_2', password='12345')
    return user_2


@pytest.fixture
def subscription_1(user_1, user_2, db):
    subscription_1 = Subscription.objects.create(user=user_1, author=user_2)
    return subscription_1


@pytest.fixture
def recipes(user_1, user_2, db):
    recipe_1 = Recipe.objects.create(
        author=user_2, name='test_recipe', cooking_time=1)
    recipe_2 = Recipe.objects.create(
        author=user_1, name='test_recipe_2', cooking_time=1)
    recipe_3 = Recipe.objects.create(
        author=user_2, name='test_recipe_3', cooking_time=1,
    )
    return recipe_1, recipe_2, recipe_3


def test_count_recipes(subscription_1, recipes, db):
    """Тест количества рецептов по подпискам"""
    recipes_count = Recipe.objects.filter(
        author=subscription_1.author).count()
    assert recipes_count == 2, 'Неверное количество рецептов'


def test_count_all_recipes(recipes, db):
    """Тест общего количества рецептов"""
    recipes_count = Recipe.objects.all().count()
    assert recipes_count == 3, 'Неверное общее количество рецептов'


def test_count_recipes_per_week(subscription_1, recipes, db):
    """Тест количества рецептов по подпискам за неделю"""
    Recipe.objects.filter(name='test_recipe_3').update(
        pub_date=(datetime.now() - timedelta(days=10)))
    recipes_count = Recipe.objects.filter(
        author=subscription_1.author,
        pub_date__gt=(datetime.now() - timedelta(days=7))
    ).count()
    assert recipes_count == 1, 'Неверное количество рецептов за неделю'


def test_message(subscription_1, recipes, db):
    """Тест текста сообщения"""
    Recipe.objects.filter(name='test_recipe_3').update(
        pub_date=(datetime.now() - timedelta(days=10)))
    recipes = Recipe.objects.filter(
        author=subscription_1.author,
        pub_date__gt=(datetime.now() - timedelta(days=7))
    )
    message = f'Добрый день, {subscription_1.author.first_name}. ' \
              f'Новые рецепты от авторов, на которых вы подписаны: \n' \
              f'{recipes[0].name} - ' \
              f'http://158.160.0.123/recipes/{recipes[0].id}\n'
    assert email(recipes, subscription_1.author) == message, (
        'Ошибка формирования сообщения'
    )
