from djoser import email

from . import tasks


class _CeleryEmailMixin(email.BaseEmailMessage):
    action: tasks.EMAIL_TYPE

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()
        context["type"] = self.action
        context["user_id"] = context.pop("user").id
        context.pop("view")
        tasks.send_email.delay(context, to)


class CeleryActivationEmail(_CeleryEmailMixin, email.ActivationEmail):
    action = "activation"


class CeleryConfirmationEmail(_CeleryEmailMixin, email.ConfirmationEmail):
    action = "confirmation"


class CeleryPasswordResetEmail(_CeleryEmailMixin, email.PasswordResetEmail):
    action = "password_reset"


class CeleryPasswordChangedConfirmationEmail(
    _CeleryEmailMixin, email.PasswordChangedConfirmationEmail
):
    action = "password_changed_confirmation"


class CeleryUsernameChangedConfirmationEmail(
    _CeleryEmailMixin, email.UsernameChangedConfirmationEmail
):
    action = "username_changed_confirmation"


class CeleryUsernameResetEmail(_CeleryEmailMixin, email.UsernameResetEmail):
    action = "username_reset"
