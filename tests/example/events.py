from datetime import datetime

from eventz.messages import Event


class ExampleEvent(Event):
    pass


class ExampleCreated(ExampleEvent):
    version: int = 1

    def __init__(
        self,
        param_one: int,
        uuid: str = None,
        timestamp: datetime = None,
    ):
        super().__init__(uuid, timestamp)
        self.param_one: int = param_one


class ExampleUpdated(ExampleEvent):
    version: int = 1

    def __init__(
        self,
        param_two: str,
        uuid: str = None,
        timestamp: datetime = None,
    ):
        super().__init__(uuid, timestamp)
        self.param_two: str = param_two
