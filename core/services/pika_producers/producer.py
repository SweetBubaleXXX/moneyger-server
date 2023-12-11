import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

import pika

T = TypeVar("T")


@dataclass
class ExchangeConfig:
    name: str
    exchange_type: Literal["direct", "fanout", "headers", "topic"]
    durable: bool = True


class Producer(Generic[T], metaclass=ABCMeta):
    def __init__(
        self,
        connection_params: pika.ConnectionParameters,
        exchange: ExchangeConfig,
    ) -> None:
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.exchange = exchange
        self.channel.exchange_declare(
            exchange.name,
            exchange.exchange_type,
            durable=exchange.durable,
        )

    def send(self, message: T) -> None:
        try:
            self._publish(message)
        except Exception:
            logging.exception("Exception occurred while publishing message")

    @abstractmethod
    def _publish(self, message: T) -> None:
        ...
