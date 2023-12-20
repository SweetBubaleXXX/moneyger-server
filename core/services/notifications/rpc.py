from contextlib import contextmanager
from typing import Iterator, Self, TypeAlias
from uuid import uuid4

import pika
from pika import connection
from pika.channel import Channel
from pika.spec import Basic

from moneymanager import notifications_service_config

from .publishers import ExchangeConfig, PublisherMessage

_SECONDS: TypeAlias = int

_RESPONSE_TIMEOUT: _SECONDS = 10


class RpcClient:
    @notifications_service_config.inject("connection_params")
    def __init__(
        self,
        connection_params: connection.Parameters,
        exchange: ExchangeConfig,
    ) -> None:
        self._connection_params = connection_params
        self._exchange = exchange
        self._connection: pika.BlockingConnection | None = None
        self._channel: Channel | None = None
        self._callback_queue = None
        self._correlation_id: str | None = None
        self._response: bytes | None = None

    def call(self, request: PublisherMessage) -> bytes:
        if not all((self._connection, self._channel)):
            raise RuntimeError("Connection and channel aren't ready")
        self._correlation_id = str(uuid4())
        self._channel.basic_publish(
            exchange=self._exchange.name,
            routing_key=request.routing_key,
            properties=pika.BasicProperties(
                reply_to=self._callback_queue,
                correlation_id=self._correlation_id,
            ),
            body=request.body,
        )
        self._connection.process_data_events(time_limit=_RESPONSE_TIMEOUT)
        if not self._response:
            raise TypeError("Got None response")
        return self._response

    @contextmanager
    def connection(self) -> Iterator[Self]:
        if self._connection:
            yield self
        else:
            yield next(self._connect_client())

    def _connect_client(self) -> Iterator[Self]:
        self._connection = pika.BlockingConnection(self._connection_params)
        try:
            self._channel = self._connection.channel()
            self._declare_exchange()
            self._declare_callback_queue()
            self._channel.basic_consume(
                queue=self._callback_queue,
                on_message_callback=self._on_response,
                auto_ack=True,
            )
            yield self
        finally:
            if self._connection.is_open:
                self._connection.close()

    def _declare_exchange(self) -> None:
        self._channel.exchange_declare(
            self._exchange.name,
            self._exchange.exchange_type,
            durable=self._exchange.durable,
        )

    def _declare_callback_queue(self) -> None:
        result = self._channel.queue_declare(queue="", exclusive=True)
        self._callback_queue = result.method.queue

    def _on_response(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        if self._correlation_id != properties.correlation_id:
            return
        self._response = body


class RpcService:
    def __init__(self, rpc_client: RpcClient) -> None:
        self.client = rpc_client
