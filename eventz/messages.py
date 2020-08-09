from datetime import datetime
from uuid import uuid4

from eventz.value_object import ValueObject


class Message(ValueObject):
    def __init__(self, uuid: str = None, timestamp: datetime = None):
        try:
            getattr(self, "version")
        except AttributeError:
            err = (
                "Child classes of Message cannot be instantiated "
                "without a 'version' attribute set on the class."
            )
            raise TypeError(err)
        self.uuid: str = uuid or str(uuid4())
        self.timestamp: datetime = timestamp or datetime.utcnow()


class Event(Message):
    pass


class Command(Message):
    pass
