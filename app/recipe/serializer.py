from rest_framework import serializers

from core.models import (
    Tag, 
    Ingredient, 
    Recipe
)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return Tag.objects.create(name=validated_data['name'], user=self.context.get('request').user)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ( 'id', 'name',)
        read_only_fields = ('id', )

    def create(self, validated_data):
        return Ingredient.objects.create(name=validated_data['name'], user=self.context['request'].user)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset= Tag.objects.all()
    )
    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes', 'image', 'price', 'link')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {key: value for key, value in data.items() if value is not None}


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)

