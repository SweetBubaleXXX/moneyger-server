from core.services.notifications.users import UsersProducer
from moneymanager import services_container

from .models import Account


@services_container.inject("users_producer")
def user_registered_receiver(
    sender,
    user: Account,
    users_producer: UsersProducer,
    **kwargs,
):
    users_producer.register_account(user).send()
