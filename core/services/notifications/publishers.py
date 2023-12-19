import logging
from collections import deque
from dataclasses import dataclass
from typing import Literal, Protocol, Type, TypeVar

import pika
from pika import connection
from pika.channel import Channel

from moneymanager import notifications_service_config

T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class ExchangeConfig:
    name: str
    exchange_type: Literal["direct", "fanout", "headers", "topic"]
    durable: bool = True


@dataclass
class PublisherMessage:
    routing_key: str
    body: str | bytes


class Publisher(Protocol):
    def __init__(
        self,
        connection_params: connection.Parameters,
        exchange: ExchangeConfig,
    ) -> None:
        ...

    def add_message(self, message: PublisherMessage) -> None:
        ...

    def publish(self) -> None:
        ...


class AsynchronousPublisher:
    _connection_class: Type[pika.BaseConnection] = pika.SelectConnection

    @notifications_service_config.inject("connection_params")
    def __init__(
        self,
        connection_params: connection.Parameters,
        exchange: ExchangeConfig,
    ) -> None:
        self._connection_params = connection_params
        self._exchange = exchange
        self._message_queue: deque[PublisherMessage] = deque()
        self._connection: pika.BaseConnection | None = None
        self._channel: Channel | None = None

    def add_message(self, message: PublisherMessage) -> None:
        self._message_queue.append(message)

    def publish(self) -> None:
        try:
            self._create_connection()
            self._connection.ioloop.start()
        except Exception:
            logger.exception("Connection failed")
            self._close_connection()
            if self._connection and not self._connection.is_closed:
                self._connection.ioloop.start()

    def _create_connection(self) -> pika.BaseConnection:
        self._connection = self._connection_class(
            self._connection_params,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed,
        )
        return self._connection

    def _close_connection(self) -> None:
        logger.info("Stopping")
        if self._channel is not None:
            self._channel.close()
        if self._connection and not self._connection.is_closed:
            self._connection.close()

    def _on_connection_open(self, connection: pika.BaseConnection) -> None:
        logger.info("Connection opened")
        connection.channel(on_open_callback=self._on_channel_open)

    def _on_connection_open_error(
        self,
        connection: pika.BaseConnection,
        exc: BaseException,
    ) -> None:
        logger.error("Failed to open connection: %s", exc)
        connection.ioloop.stop()

    def _on_connection_closed(
        self,
        connection: pika.BaseConnection,
        exc: BaseException,
    ) -> None:
        logger.info("Connection closed: %s", exc)
        self._channel = None
        connection.ioloop.stop()

    def _on_channel_open(self, channel: Channel) -> None:
        logger.info("Channel opened")
        self._channel = channel
        self._channel.add_on_close_callback(self._on_channel_closed)
        self._setup_exchange()

    def _on_channel_closed(self, channel: Channel, reason) -> None:
        logger.info("Channel %i was closed: %s", channel, reason)
        self._channel = None

    def _setup_exchange(self) -> None:
        logger.info("Declaring exchange: %s", self._exchange.name)
        self._channel.exchange_declare(
            exchange=self._exchange.name,
            exchange_type=self._exchange.exchange_type,
            durable=self._exchange.durable,
            callback=self._on_exchange_declared,
        )

    def _on_exchange_declared(self, _frame) -> None:
        logger.info("Exchange declared: %s", self._exchange.name)
        self._publish_messages()

    def _publish_messages(self) -> None:
        if self._channel is None or not self._channel.is_open:
            return self._close_connection()
        message_properties = pika.BasicProperties(
            app_id="moneyger-server",
        )
        while self._message_queue:
            message = self._message_queue.popleft()
            self._channel.basic_publish(
                self._exchange.name,
                message.routing_key,
                message.body,
                message_properties,
            )
        logger.info("Messages published")
        self._close_connection()
