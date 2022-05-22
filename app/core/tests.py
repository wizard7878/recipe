from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from . import models

def sample_user():
    user = get_user_model().objects.create_user(
        email='test@prp.com',
        password='testpass123'
    )

    return user

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = 'test@prp.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        

    def test_new_user_email_normalized(self):
        email = 'test@prp.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '13245646545')

    def test_create_new_super_user(self):
        user = get_user_model().objects.create_superuser('prp@email.com', 'test123456')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_ingredient_str(self):
        ingredient = models.Ingredient.objects.create(
            user= sample_user(),
            name="Cucumber"
        )

        self.assertEqual(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        recpie = models.Recipe.objects.create(
            user = sample_user(),
            title= "steak and mushroom sauce",
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recpie), recpie.title)
    



class AdminSiteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser('prp@email.com', 'test123456')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@email.com',
            password='pass123456',
            name = 'user'
        )

    def test_users_listed(self):
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)