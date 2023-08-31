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
