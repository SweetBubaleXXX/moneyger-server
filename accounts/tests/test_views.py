import jwt
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from core.services.notifications.users import AccountCredentials
from core.tests import MockPublishersMixin

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

    def test_logout_unauthorized(self):
        response = self.client.post(reverse("token_logout"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_cookie(self):
        client = Client()
        client.force_login(self.account)
        response = client.post(reverse("token_logout"))
        refresh_token_cookie = response.cookies[settings.JWT_REFRESH_TOKEN_COOKIE]
        self.assertFalse(refresh_token_cookie.value)

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


class TestUserViewSet(MockPublishersMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.account = AccountFactory.build()

    def test_user_registered_signal(self):
        response = self.client.post(
            reverse("users-list"),
            {
                "username": self.account.username,
                "email": self.account.email,
                "password": DEFAULT_ACCOUNT_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.publisher_mock.add_message.assert_called_once()
        self.publisher_mock.publish.assert_called_once()

    def test_user_deleted_notification(self):
        saved_account = AccountFactory()
        self.client.force_login(saved_account)
        response = self.client.delete(
            reverse("users-me"),
            {"current_password": DEFAULT_ACCOUNT_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.publisher_mock.add_message.assert_called_once()
        self.publisher_mock.publish.assert_called_once()


class NotificationsServiceAuthViewTests(MockPublishersMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.account = AccountFactory()
        self.token_secret = "secret"
        self.users_rpc_mock.get_account_credentials.return_value = AccountCredentials(
            account_id=self.account.id,
            email=self.account.email,
            token=self.token_secret,
        )

    def test_get_token_unauthorized(self):
        response = self.client.get(reverse("notifications-service-token"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_jwt_token(self):
        self.client.force_login(self.account)
        response = self.client.get(reverse("notifications-service-token"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jwt_token = response.json()["access_token"]
        token_payload = jwt.decode(
            jwt_token,
            key=self.token_secret,
            algorithms=["HS256"],
        )
        self.assertEqual(token_payload["account_id"], self.account.id)
