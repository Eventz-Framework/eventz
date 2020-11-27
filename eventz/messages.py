from datetime import datetime
from uuid import uuid4

from eventz.value_object import ValueObject


class Message(ValueObject):
    def __init__(self, __msgid__: str = None, __timestamp__: datetime = None):
        try:
            getattr(self, "__version__")
        except AttributeError:
            err = (
                "Child classes of Message cannot be instantiated "
                "without a '__version__' attribute set on the class."
            )
            raise TypeError(err)
        self.__msgid__: str = __msgid__ or str(uuid4())
        self.__timestamp__: datetime = __timestamp__ or datetime.utcnow()


class Event(Message):
    pass


class Command(Message):
    pass
