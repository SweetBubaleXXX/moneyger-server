import json
from typing import Self

from ..messages import SerializedMessage
from .producer import Producer
from .publishers import PublisherMessage


class MessagesProducer(Producer):
    def add_new_message(self, message: SerializedMessage) -> Self:
        self.publisher.add_message(
            PublisherMessage(
                routing_key="message.event.sent",
                body=json.dumps(message),
            )
        )
        return self
