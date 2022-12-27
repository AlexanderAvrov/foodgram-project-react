import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

from recipes.models import (Recipe, Tag, Ingredient, IngredientRecipe,
                              Subscription, Favorite, TagRecipe)
from shopping_cart.models import ShoppingCart
from users.models import User


class JWTTokenSerializer(serializers.Serializer):
    """Сериалайзер для получения токена"""

    password = serializers.CharField()
    email = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(
                email=data['email'], password=data['password']).exists():
            raise exceptions.NotFound(
                'Такого пользователя не существует, или неверный пароль')

        return data


class UserReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения пользователя"""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Метод определения подписки на автора"""
        request = self.context.get('request')
        if request.user.is_anonymous or request.user == obj:
            return False
        return Subscription.objects.filter(
                    user=request.user, author=obj).exists()


class UserPostSerializer(serializers.ModelSerializer):
    """Сериалайзер для регистрации пользователя"""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингредиентов"""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeAddSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления рецептов"""

    tags = serializers.ListField()
    image = Base64ImageField()
    ingredients = serializers.ListField()
    author = serializers.ReadOnlyField(required=False)

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data):
        for ingredient in data.get('ingredients'):
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            tag_object = get_object_or_404(Tag, id=tag)
            TagRecipe.objects.create(tag=tag_object, recipe=recipe)
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient.get('id'))
            IngredientRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=recipe, amount=ingredient.get('amount'))
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', instance.tags)
        ingredients = validated_data.pop('ingredients', instance.ingredients)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for tag in tags:
            tag_object = get_object_or_404(Tag, id=tag)
            TagRecipe.objects.create(tag=tag_object, recipe=instance)
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient.get('id'))
            IngredientRecipe.objects.create(
                ingredient=ingredient_obj,
                recipe=instance, amount=ingredient.get('amount'))
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeSerializer(instance, context={'request': request})
        return serializer.data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов"""

    author = UserReadSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        source='recipe_from_ingredient', many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('tags', 'author', 'ingredients')

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0')
        return value

    def get_is_favorited(self, obj):
        """Метод определения рецепта в избранном"""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод определения рецепта в избранном"""
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient.get('id'),
                recipe=recipe, amount=ingredient.get('amount'))
        return recipe

    def update(self, instance, validated_data):
        pass

class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого вывода рецептов"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для избранного"""

    class Meta:
        fields = ()
        model = Favorite

    def to_representation(self, instance):
        recipe = instance.recipe
        serializer = RecipeSmallSerializer(recipe)
        return serializer.data


"""
class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ()
        model = Subscription

    def to_representation(self, author):
        request = self.context.get('request')
        serializer = SubscriptionsSerializer(author, request)
        if serializer.is_valid():
            return serializer.data
"""


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения всех подписок"""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = Subscription

    def get_is_subscribed(self, obj):
        """Метод определения подписки на автора"""
        request = self.context.get('request')
        if request.user == obj.author:
            return False
        return Subscription.objects.filter(
                    user=request.user, author=obj.author).exists()

    def get_recipes(self, obj):
        """Метод получения рецептов автора"""
        queryset = Recipe.objects.filter(author=obj.author).all()
        serializer = RecipeSmallSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Метод получения рецептов автора"""
        return obj.author.recipes.count()
