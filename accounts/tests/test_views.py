from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import DEFAULT_ACCOUNT_PASSWORD, AccountFactory


class JwtViewsTestCase(TestCase):
    def setUp(self):
        self.account = AccountFactory()

    def test_csrf_token_required(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("token_refresh"), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_token_view(self):
        refresh_token = RefreshToken.for_user(self.account)
        self.client.cookies[settings.JWT_REFRESH_TOKEN_COOKIE] = str(refresh_token)
        response = self.client.post(reverse("token_refresh"), {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

    def test_refresh_token_cookie(self):
        self._obtain_token_request()
        self.assertIn(settings.JWT_REFRESH_TOKEN_COOKIE, self.client.cookies)

    def test_csrf_token_cookie(self):
        self._obtain_token_request()
        self.assertIn("csrftoken", self.client.cookies)

    def _obtain_token_request(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "username": self.account.username,
                "password": DEFAULT_ACCOUNT_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response
