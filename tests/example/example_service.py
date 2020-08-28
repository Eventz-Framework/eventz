from typing import Tuple

from eventz.messages import Command, Event
from eventz.service import Service
from tests.example.commands import CreateExample, UpdateExample
from tests.example.example_aggregate import ExampleAggregate


class ExampleService(Service):
    def process(self, command: Command) -> Tuple[Event, ...]:
        if isinstance(command, CreateExample):
            return self._create_example(command)
        elif isinstance(command, UpdateExample):
            return self._update_example(command)

    def _create_example(self, command: CreateExample) -> Tuple[Event, ...]:
        return self._repository.create(
            uuid=command.example_id,
            param_one=command.param_one,
            param_two=command.param_two,
        )

    def _update_example(self, command: UpdateExample) -> Tuple[Event, ...]:
        example: ExampleAggregate = self._repository.read(command.example_id)
        events = example.update(
            param_one=command.param_one, param_two=command.param_two
        )
        self._repository.persist(aggregate_id=command.example_id, events=events)
        return events
