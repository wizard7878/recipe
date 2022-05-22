import tempfile, os
from PIL import Image
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Recipe, Tag, Ingredient
from ..serializer import RecipeSerializer, RecipeDetailSerializer


recipe_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name="Main course"):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicrecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(recipe_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivaterecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@email.com",
            password="qwerty12345"
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(recipe_URL)
        # self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            email="example2@email.com",
            password="qwerty12345"
        )

        sample_recipe(user=user2, title='Cake recipe')
        sample_recipe(user=self.user)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        res = self.client.get(recipe_URL)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_basic_recipe(self):
        payload = {
            'title': 'chocolate cheeasCake',
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(recipe_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1=sample_tag(user=self.user, name="Vegan")
        tag2=sample_tag(user=self.user, name="Dessert")

        payload = {
            'title': 'chocolate cheeasCake',
            'time_minutes': 30,
            'price': 30.00,
            'tags' : [tag1.id, tag2.id]
        }

        res = self.client.post(recipe_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'chocolate cheeasCake',
            'time_minutes': 30,
            'price': 30.00,
            'ingredients' : [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(recipe_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)

    def test_partial_update_recipe(self):
        recipe= sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user= self.user, name='Curry')

        payload = {
            'title': 'Chicken', 'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        recipe= sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title' : "Spaghetti",
            'time_minutes': 25,
            'price': 5.00
        }

        url = detail_url(recipe.id)
        self.client.put(url , payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])    
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])    
        self.assertEqual(recipe.price, payload['price'])    
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@email.com",
            password="qwerty12345"
        )

        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    # def test_upload_image_to_recipe(self):
    #     url = image_upload_url(self.recipe.id)
    #     with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
    #         img = Image.new('RGB', (10,10))
    #         img.save(ntf, format='JPGE')
    #         ntf.seek(0)
    #         res = self.client.post(url, {'image': ntf}, format='multipart')

    #     self.recipe.refresh_from_db()
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('image', res.data)
    #     self.assertTrue(os.path.exists(self.recipe.image.path))

    # def test_upload_image_bad_request(self):
    #     url = image_upload_url(self.recipe)
    #     res = self.client.post(url, {'image': None}, format='multipart')
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        recipe1 = sample_recipe(self.user, title='Vegetable celery')
        recipe2 = sample_recipe(self.user, title='Vegetable celery')
        tag1 = sample_tag(self.user, name="Vegan")
        tag2 = sample_tag(self.user, name="Vegetarian")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(self.user, title="Fish and chips")

        res = self.client.get(
            recipe_URL,
            {'tags' : f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data) 

    def test_filter_recipes_by_ingredients(self):
        
        recipe1 = sample_recipe(self.user, title='pizza')
        recipe2 = sample_recipe(self.user, title='sandwitch')
        ingredient1 = sample_ingredient(self.user, name='meat')
        ingredient2 = sample_ingredient(self.user, name='mushrooms')     
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)   
        recipe3 = sample_recipe(self.user, title='bnana cake')

        res = self.client.get(
            recipe_URL, 
            {'ingredients' : f'{ingredient1.id}, {ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)                