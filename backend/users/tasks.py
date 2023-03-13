from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail

from recipes.models import Subscription, Recipe
from users.models import User


def email(recipes, recipient):
    """Формирование текста письма и отправка письма"""
    links = f'Добрый день, {recipient.first_name}. ' \
            f'Новые рецепты от авторов, на которых вы подписаны: \n'
    for recipe in recipes:
        links += f'{recipe.name} - http://158.160.0.123/recipes/{recipe.id}\n'
    send_mail(subject='Новые публикации на Foodgram', message=links,
              recipient_list=[recipient.email], from_email='admin@foogram.com',
              fail_silently=True)
    return links


@shared_task
def new_recipes():
    """Отбор новых рецептов для подписчиков"""
    users = User.objects.filter(subscriber__isnull=False)
    for user in users:
        subscriptions = Subscription.objects.filter(user=user)
        if subscriptions:
            recipes = []
            for subscription in subscriptions:
                recipes += Recipe.objects.filter(
                    author=subscription.author,
                    pub_date__gte=(datetime.now().date() - timedelta(days=7))
                )
            if recipes:
                email(recipes, user)
