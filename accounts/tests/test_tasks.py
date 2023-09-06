from django.core import mail
from django.test import TestCase

from .. import tasks
from .factories import AccountFactory


class SendMailTaskTests(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.context = {
            "user_id": self.account.id,
            "domain": "domain.local",
            "protocol": "http",
            "site_name": "domain.local",
            "uid": "uid",
            "token": "token",
            "url": "http://domain.local/uid/token/",
        }

    def test_activation(self):
        self._test_action(
            "activation", f'Account activation on {self.context["domain"]}'
        )

    def test_confirmation(self):
        self._test_action(
            "confirmation",
            "{} - Your account has been successfully created and activated!".format(
                self.context["domain"]
            ),
        )

    def test_password_reset(self):
        self._test_action(
            "password_reset", f'Password reset on {self.context["domain"]}'
        )

    def test_password_changed_confirmation(self):
        self._test_action(
            "password_changed_confirmation",
            f'{self.context["domain"]} - Your password has been successfully changed!',
        )

    def test_username_changed_confirmation(self):
        self._test_action(
            "username_changed_confirmation",
            f'{self.context["domain"]} - Your username has been successfully changed!',
        )

    def test_username_reset(self):
        self._test_action(
            "username_reset", f'Username reset on {self.context["domain"]}'
        )

    def _test_action(self, action: tasks.EMAIL_TYPE, expected_subject: str):
        context = self._create_context(action)
        tasks.send_email(context, [self.account.email])
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertListEqual(sent_email.to, [self.account.email])
        self.assertEqual(sent_email.subject, expected_subject)

    def _create_context(self, action: tasks.EMAIL_TYPE) -> tasks.EmailContext:
        return self.context | {"type": action}
