from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import SlidingToken, RefreshToken

from .filters import IngredientFilter, RecipeFilter
from .permissions import OwnerOrReadPermission
from .mixins import PostDeleteViewSet, ListViewSet
from .serializers import (
    JWTTokenSerializer, UserReadSerializer, UserPostSerializer,
    IngredientSerializer, RecipeSerializer, TagSerializer, FavoriteSerializer,
    SubscriptionsSerializer, RecipeSmallSerializer, RecipeAddSerializer)
from recipes.models import Recipe, Tag, Ingredient, Subscription, Favorite
from shopping_cart.models import ShoppingCart
from users.models import User


class RecipeViewSet(viewsets.ModelViewSet):
    """Вью сет для рецептов"""

    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = (OwnerOrReadPermission,)
    # serializer_class = RecipeSerializer
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

    def delete(self, request, recipe_id):  # TODO: прописать 400-е ошибки
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()

        return Response({'message': 'Рецепт успешно удален из корзины'},
                        status=status.HTTP_204_NO_CONTENT)


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
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()

        return Response({'message': 'Рецепт успешно удален из избранного'},
                        status=status.HTTP_204_NO_CONTENT)


class SubscribeAPIView(APIView):
    """Вью сет для подписок"""

    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):   # TODO: сделать сериализатор для отображения после публикации
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

    def delete(self, request, user_id):  # TODO: прописать 400-е ошибки
        author = get_object_or_404(User, id=user_id)
        Subscription.objects.filter(user=request.user, author=author).delete()

        return Response({'message': 'Подписка успешно удалена'},
                        status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListAPIView(ListAPIView):
    """Вью класс для просмотра списка подписок"""

    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.subscriber.all()


class UserViewSet(viewsets.ModelViewSet):
    """Вью сет для пользователей"""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Определение сериалайзера для пользователей"""
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserPostSerializer

    @action(detail=False, methods=('get',),
            url_name='me', permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        serializer = UserReadSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=('post',),
            url_name='set_password', permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        serializer = UserPostSerializer(
            request.user, data=request.data, partial=True, many=False)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK)

"""
    @action(detail=False, methods=('get',),
            url_name='subscriptions', permission_classes=(IsAuthenticated,))
    def subscriptions(self, request, *args, **kwargs):
        subscriptions = User.objects.filter(author_recipes__user=request.user.id).all()
        queryset = self.request.user.subscriber.all()
        serializer = SubscribtionsSerializer(context={'request': request}, many=True)
        return Response(serializer.data)
"""


class APIToken(APIView):
    """Вью класс для получения токена"""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = JWTTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=serializer.data['email'])
        token = SlidingToken.for_user(user)

        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class Logout(APIView):
    """Вью класс для удаления токена"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.auth
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
