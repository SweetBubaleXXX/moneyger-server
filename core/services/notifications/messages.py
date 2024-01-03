import json
from typing import Self

from ..messages import SerializedMessage
from .producer import Producer
from .publishers import PublisherMessage


class MessagesProducer(Producer):
    def add_new_message(self, message: SerializedMessage) -> Self:
        message_body = {
            "id": message["message_id"],
            "sender": message["user"],
            "from_admin": message["is_admin"],
            "text": message["message_text"],
            "timestamp": message["timestamp"],
        }
        self.publisher.add_message(
            PublisherMessage(
                routing_key="message.event.sent",
                body=json.dumps(message_body),
            )
        )
        return self
