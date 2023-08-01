from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class TransactionCategoryViewTests(TestCase):
    def test_unauthorized(self):
        response = self.client.get(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
