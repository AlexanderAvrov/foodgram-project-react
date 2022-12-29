from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import CustomPagination
from recipes.models import Favorite, Ingredient, Recipe, Subscription, Tag
from shopping_cart.download_cart import download_ingredients
from shopping_cart.models import ShoppingCart
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerOrReadPermission
from .serializers import (IngredientSerializer, RecipeAddSerializer,
                          RecipeSerializer, RecipeSmallSerializer,
                          SubscriptionsSerializer, TagSerializer,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью сет для рецептов"""

    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = (OwnerOrReadPermission,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определение сериалайзера для пользователей"""
        if self.action in ('create', 'partial_update'):
            return RecipeAddSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Переопределение метода создания поста"""
        serializer.save(author=self.request.user)

    @action(detail=False, methods=('get',),
            url_name='download_shopping_cart', permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод для скачивания списка покупок"""
        ingredients = download_ingredients(request.user)
        return HttpResponse(
            ingredients,
            content_type='text/plain,charset=utf8',
            status=status.HTTP_200_OK,
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью сет для тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью сет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class ShoppingCartAPIView(APIView):
    """Вью сет для списка покупок"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, recipe_id):
        """Метод для добавления в избранное"""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).exists():
            return Response(
                {'error': 'Вы уже добавили этот рецепт в корзину'},
                status=status.HTTP_400_BAD_REQUEST)
        cart = ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeSmallSerializer(cart.recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        """Метод удаления рецепта из списка покупок"""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        cart = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        if cart:
            cart.delete()
            return Response({'message': 'Рецепт успешно удален из корзины'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Рецепта не было в корзине'},
                        status=status.HTTP_400_BAD_REQUEST)


class FavoriteAPIView(APIView):
    """Вью сет для избранного"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, recipe_id):
        """Метод для добавления в избранное"""
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(
                user=request.user, recipe=recipe).exists():
            return Response(
                {'error': 'Вы уже добавили этот рецепт в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        favorite = Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeSmallSerializer(favorite.recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):  # TODO: прописать 400-е ошибки
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favor = Favorite.objects.filter(user=request.user, recipe=recipe)
        if favor:
            favor.delete()
            return Response({'message': 'Рецепт успешно удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Рецепта не было в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscribeAPIView(APIView):
    """Вью сет для подписок"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        """Метод для создания экземпляра подписки"""
        author = get_object_or_404(User, id=user_id)
        if self.request.user == author or Subscription.objects.filter(
                user=request.user, author=author).exists():
            return Response(
                {'error': 'Вы пытаетесь подписаться на самого '
                 'себя или уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.create(author=author, user=self.request.user)
        serializer = SubscriptionsSerializer(subscription, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        obj = Subscription.objects.filter(user=request.user, author=author)
        if obj:
            obj.delete()
            return Response({'message': 'Подписка успешно удалена'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'У вас не было такой подписки'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsListAPIView(ListAPIView):
    """Вью класс для просмотра списка подписок"""

    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return user.subscriber.all()
