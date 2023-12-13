import logging
from typing import AnyStr, TypeVar

from .publishers import Message, Publisher

T = TypeVar("T")


class Producer:
    def __init__(self, publisher: Publisher) -> None:
        self.publisher: Publisher = publisher

    def send(self, routing_key: str, body: AnyStr) -> None:
        try:
            message = Message(routing_key, body)
            self.publisher.add_message(message)
            self.publisher.publish()
        except Exception:
            logging.exception("Exception occurred while publishing message")
