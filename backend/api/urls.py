from django.urls import include, path
from rest_framework import routers

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet,
                    FavoriteAPIView, SubscribeAPIView, APIToken, Logout,
                    SubscriptionsListAPIView, ShoppingCartAPIView)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('recipes', RecipeViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
# router_v1.register('users', UserViewSet)
# router_v1.register(
#    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
#    basename='favorite')

"""
urlpatterns_auth = [
    path('login/', APIToken.as_view(), name='token'),
    path('logout/', Logout.as_view(), name='logout'),
]
"""

urlpatterns = [
    path('users/subscriptions/', SubscriptionsListAPIView.as_view(),
         name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
    path('users/<int:user_id>/subscribe/',
         SubscribeAPIView.as_view(), name='subscribe'),
    path('recipes/<int:recipe_id>/favorite/', FavoriteAPIView.as_view(),
         name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartAPIView.as_view(),
         name='shopping_cart'),
]
