import asyncio
import typing
import logging
from urllib.parse import urlparse

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from .._base import Event
from .base import BroadcastBackend


class KafkaBackend(BroadcastBackend):
    def __init__(self, url: str):
        print('****** KafkaBackend INIT ******')
        logging.warning('****** KafkaBackend INIT ******')
        self._servers = [
            urlparse(url).netloc
        ]  # TODO: update to parse multiple values to a list
        self._consumer_channels: typing.Set = set()
        self._security_protocol = os.environ.get("KAFKA_SECURITY_PROTOCOL") or "PLAIN"
        self._sasl_mechanism = os.environ.get("KAFKA_SASL_MECHANISM") or "PLAIN"
        self._sasl_plain_username = os.environ.get("KAFKA_PLAIN_USERNAME")
        self._sasl_plain_password = os.environ.get("KAFKA_PLAIN_PASSWORD")

    async def connect(self) -> None:
        print('******** I AM IN BROADCASTER ********')
        logging.warning('******** I AM IN BROADCASTER ********')
        logging.warning("self._servers ---> ", self._servers)
        logging.warning("self._security_protocol --->", self._security_protocol)
        logging.warning("self._sasl_mechanism --->", self._sasl_mechanism)
        logging.warning("self._sasl_plain_username --->", self._sasl_plain_username)

        loop = asyncio.get_event_loop()
        self._producer = AIOKafkaProducer(
            loop=loop,
            bootstrap_servers=self._servers,
            # security_protocol=self._security_protocol,
            # sasl_mechanism=self._sasl_mechanism,
            # sasl_plain_username=self._sasl_plain_username,
            # sasl_plain_password=self._sasl_plain_password,
        )
        self._consumer = AIOKafkaConsumer(
            loop=loop,
            bootstrap_servers=self._servers,
            # security_protocol=self._security_protocol,
            # sasl_mechanism=self._sasl_mechanism,
            # sasl_plain_username=self._sasl_plain_username,
            # sasl_plain_password=self._sasl_plain_password,
        )
        await self._producer.start()
        await self._consumer.start()

    async def disconnect(self) -> None:
        await self._producer.stop()
        await self._consumer.stop()

    async def subscribe(self, channel: str) -> None:
        self._consumer_channels.add(channel)
        self._consumer.subscribe(topics=self._consumer_channels)

    async def unsubscribe(self, channel: str) -> None:
        await self._consumer.unsubscribe()

    async def publish(self, channel: str, message: typing.Any) -> None:
        await self._producer.send_and_wait(channel, message.encode("utf8"))

    async def next_published(self) -> Event:
        message = await self._consumer.getone()
        return Event(channel=message.topic, message=message.value.decode("utf8"))
