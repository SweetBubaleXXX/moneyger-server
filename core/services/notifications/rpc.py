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
        if not (self._connection and self._connection.is_open):
            raise RuntimeError("Connection is not open")
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
    def connect(self) -> Iterator[Self]:
        try:
            yield self._create_connection()
        finally:
            if self._connection and self._connection.is_open:
                self._connection.close()

    def _create_connection(self) -> Self:
        self._connection = pika.BlockingConnection(self._connection_params)
        self._channel = self._connection.channel()
        self._declare_exchange()
        self._declare_callback_queue()
        self._channel.basic_consume(
            queue=self._callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )
        return self

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
        self._client = rpc_client
