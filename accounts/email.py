from djoser import email

from . import tasks


class _CeleryEmailMixin(email.BaseEmailMessage):
    def _get_serializable_context(self):
        context = self.get_context_data()
        context["user_id"] = context.pop("user").id
        context.pop("view")
        return context


class CeleryActivationEmail(_CeleryEmailMixin, email.ActivationEmail):
    def send(self, to, *args, **kwargs):
        context = self._get_serializable_context()
        tasks.send_activation_email.delay(context, to)
