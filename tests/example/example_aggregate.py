from datetime import datetime
from typing import Optional, Tuple

from eventz.aggregate import Aggregate
from eventz.messages import Event


class ExampleAggregate(Aggregate):
    def __init__(
        self, uuid: str, param_one: int, param_two: str,
    ):
        super().__init__(uuid)
        self.param_one: int = param_one
        self.param_two: str = param_two

    @classmethod
    def create(cls, uuid: str, param_one: int, param_two: str,) -> Tuple[Event, ...]:
        return (
            ExampleCreated(aggregate_id=uuid, param_one=param_one, param_two=param_two),
        )

    def update(self, param_one: int, param_two: str) -> Tuple[Event, ...]:
        return (
            ExampleUpdated(
                aggregate_id=self.uuid, param_one=param_one, param_two=param_two
            ),
        )


class ExampleEvent(Event):
    pass


class ExampleCreated(ExampleEvent):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        param_one: int,
        param_two: str,
        __msgid__: str = None,
        __timestamp__: datetime = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__, __seq__)
        self.param_one: int = param_one
        self.param_two: str = param_two


class ExampleUpdated(ExampleEvent):
    __version__: int = 1

    def __init__(
        self,
        aggregate_id: str,
        param_one: int,
        param_two: str,
        __msgid__: str = None,
        __timestamp__: datetime = None,
        __seq__: Optional[int] = None,
    ):
        super().__init__(aggregate_id, __msgid__, __timestamp__, __seq__)
        self.param_one: int = param_one
        self.param_two: str = param_two
