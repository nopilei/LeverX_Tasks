from api.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestCreateUsers(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('users-list')
        cls.credentials = {'username': 'test', 'password': 'password'}

    def test_create_student(self):
        response = self.client.post(self.url, {**self.credentials, 'role': 'S'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lecturer(self):
        response = self.client.post(self.url, {**self.credentials, 'role': 'L'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid(self):
        response = self.client.post(self.url, {**self.credentials, 'role': 'SL'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

