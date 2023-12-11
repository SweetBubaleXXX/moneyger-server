import logging
from dataclasses import dataclass
from typing import AnyStr, Literal, TypeVar

import pika

T = TypeVar("T")


@dataclass
class ExchangeConfig:
    name: str
    exchange_type: Literal["direct", "fanout", "headers", "topic"]
    durable: bool = True


class Producer:
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

    def publish(self, routing_key: str, body: AnyStr) -> None:
        try:
            self.channel.basic_publish(self.exchange.name, routing_key, body)
        except Exception:
            logging.exception("Exception occurred while publishing message")
