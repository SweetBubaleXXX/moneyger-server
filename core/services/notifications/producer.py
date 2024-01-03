import logging
from typing import TypeVar

from .publishers import Publisher

T = TypeVar("T")


class Producer:
    def __init__(self, publisher: Publisher) -> None:
        self.publisher: Publisher = publisher

    def send(self) -> None:
        try:
            self.publisher.publish()
        except Exception:
            logging.exception("Exception occurred while publishing messages")
