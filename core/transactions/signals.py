from django.db.models.signals import post_save
from django.dispatch import receiver

from core.services.notifications.transactions import TransactionsProducer
from moneymanager import services_container

from .models import Transaction


@receiver(post_save, sender=Transaction)
@services_container.inject("transactions_producer")
def transaction_added_notification(
    sender,
    instance: Transaction,
    created: bool,
    transactions_producer: TransactionsProducer,
    **kwargs,
):
    transactions = (instance,)
    if created:
        transactions_producer.add_transactions(transactions)
    else:
        transactions_producer.update_transactions(transactions)
