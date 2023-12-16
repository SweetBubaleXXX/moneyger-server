import asyncio
from concurrent.futures import ThreadPoolExecutor

from moneymanager import services_container

from ..services.messages import SerializedMessage
from ..services.notifications.messages import MessagesProducer


@services_container.inject("messages_producer")
async def notify_new_message(
    message: SerializedMessage,
    messages_producer: MessagesProducer,
):
    messages_producer.add_new_message(message)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, messages_producer.send)
