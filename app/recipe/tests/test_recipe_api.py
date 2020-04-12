from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    default = {
        'title': "New recipe",
        'time_minutes': 10,
        'price': 4.00
    }
    default.update(params)

    return Recipe.objects.create(user=user, **default)


class PublicRecipeApiTests(TestCase):
    """Test public Recipe API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test recipe retrieving requires login"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated user recipe API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "testmail@mail.com",
            "testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test recipes retrieving"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test that recipes list is shown only to the owner"""
        user2 = get_user_model().objects.create_user(
            "other@mail.com",
            "passsssss"
        )
        sample_recipe(user2)
        sample_recipe(self.user, title="BestRecipe")
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)