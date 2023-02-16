import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Subscription, Tag, TagRecipe)
from shopping_cart.models import ShoppingCart
from users.models import User


class UserReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для получения пользователя"""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Метод определения подписки на автора"""
        request = self.context.get('request')
        return (not request.user.is_anonymous and request.user != obj
                and Subscription.objects.filter(
                    user=request.user, author=obj).exists())


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
    """Сериалайзер для количества ингредиентов в рецепте"""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class Base64ImageField(serializers.ImageField):
    """Сериалайзер для преобразования картинок из строк base64"""
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
        """Метод проверки данных"""
        if data['cooking_time'] <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        ingredients = []
        for ingredient in data.get('ingredients'):
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.')
            id_ingredient = ingredient.get('id')
            if id_ingredient in ingredients:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться.')
            ingredients.append(id_ingredient)
        return data

    def create_tags_ingredients_objects(self, tags, ingredients, recipe):
        """Метод для создания Тегов и Ингредиентов для Рецептов"""
        TagRecipe.objects.bulk_create([
            TagRecipe(tag=get_object_or_404(Tag, id=tag),
                      recipe=recipe) for tag in tags])
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(ingredient=get_object_or_404(
                Ingredient, id=ingredient.get('id')), recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients])

    def create(self, validated_data):
        """Метод создания рецепта"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags_ingredients_objects(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта"""
        tags = validated_data.pop('tags', instance.tags)
        ingredients = validated_data.pop('ingredients', instance.ingredients)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.create_tags_ingredients_objects(tags, ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод переопределяющий вывод информации"""
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

    def get_is_favorited(self, obj):
        """Метод определения рецепта в избранном"""
        request = self.context.get('request')
        return (not request.user.is_anonymous
                and Favorite.objects.filter(
                    user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        """Метод определения рецепта в избранном"""
        request = self.context.get('request')
        return (not request.user.is_anonymous
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj).exists())


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого вывода рецептов"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


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
        return (not request.user == obj.author
                and Subscription.objects.filter(
                    user=request.user, author=obj.author).exists())

    def get_recipes(self, obj):
        """Метод получения рецептов автора"""
        request = self.context.get('request')
        if request.GET.get('recipes_limit'):
            recipe_limit = int(request.GET.get('recipes_limit'))
            queryset = Recipe.objects.filter(
                author=obj.author).all()[:recipe_limit]
        else:
            queryset = Recipe.objects.filter(author=obj.author).all()
        serializer = RecipeSmallSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Метод получения рецептов автора"""
        return obj.author.recipes.count()
