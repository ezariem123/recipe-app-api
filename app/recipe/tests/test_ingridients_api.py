from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingridient

from recipe.serializers import IngridientSerializer


INGRIDEINTS_URL = reverse('recipe:ingridient-list')


class PublicIngridientsApiTests(TestCase):
    """TEsts the publicly available ingridients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGRIDEINTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngridientsApiTests(TestCase):
    """Tests the private ingridients API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@mail.pl',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingridients_list(self):
        """Tests retrieving the list of ingridients"""
        Ingridient.objects.create(user=self.user, name='Kale')
        Ingridient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGRIDEINTS_URL)

        ingridients = Ingridient.objects.all().order_by('-name')
        serializer = IngridientSerializer(ingridients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingriients_limited_to_user(self):
        """Test that ingridients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'otheruser@mail.pl',
            'qwerty123'
        )
        Ingridient.objects.create(user=user2, name='Vinegar')

        ingridient = Ingridient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGRIDEINTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingridient.name)
