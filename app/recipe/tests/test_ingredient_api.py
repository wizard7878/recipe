from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from core.models import Ingredient
from recipe.serializer import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientApiTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email= "peyman@gmail.com",
            password="123456789"
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        Ingredient.objects.create(name="some staff", user=self.user)
        Ingredient.objects.create(name="Salt", user=self.user)
        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            email= "user2@gmail.com",
            password="123456789"
        )

        Ingredient.objects.create(name="some staff", user=user2)
        ingredient = Ingredient.objects.create(name="Salt", user=self.user)
        res = self.client.get(INGREDIENT_URL)
 
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(len(res.data), 1)

    def test_create_ingredient_successfull(self):
        payload = {
            'name': 'garlic',
        }
        res = self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(name=payload['name']).exists()

        self.assertTrue(exists)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload["name"])

    def test_create_ingredient_invalid(self):
        payload = {
            'name': '',
        }
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)