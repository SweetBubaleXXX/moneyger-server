from uuid import uuid4

import factory

from ..services import SerializedMessage


class MessageFactory(factory.Factory):
    class Meta:
        model = SerializedMessage

    message_id = factory.LazyFunction(lambda: str(uuid4()))
    user = factory.Faker("first_name")
    is_admin = False
    message_text = factory.Faker("sentence")
    timestamp = factory.Faker("unix_time")
