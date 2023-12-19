from moneymanager import services_container

from ..services.messages import SerializedMessage
from ..services.notifications.messages import MessagesProducer


@services_container.inject("messages_producer")
def notify_new_message(
    message: SerializedMessage,
    messages_producer: MessagesProducer,
):
    messages_producer.add_new_message(message).send()
