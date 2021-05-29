from typing import Tuple

from eventz.commands import SnapshotCommand
from eventz.messages import Command, Event
from eventz.service import Service
from tests.example.commands import CreateExample, UpdateExample
from tests.example.example_aggregate import ExampleAggregate, ExampleSnapshot


class ExampleService(Service):
    def _get_standard_commands(self) -> Tuple[str, ...]:
        return (
            "commands.example.CreateExample",
            "commands.example.UpdateExample",
        )

    def _process_domain_commands(self, command: Command) -> Tuple[Event, ...]:
        if isinstance(command, CreateExample):
            return self._create_example(command)
        elif isinstance(command, UpdateExample):
            return self._update_example(command)

    def _snapshot_command(self, command: SnapshotCommand) -> Tuple[Event, ...]:
        example, seq = self._repository.read(aggregate_id=command.aggregate_id)
        snapshot_events = (
            ExampleSnapshot(
                aggregate_id=example.uuid,
                param_one=example.param_one,
                param_two=example.param_two,
            ),
        )
        # persist the snapshot -
        # eventually we can use these events to make retrieval more efficient
        return self._repository.persist(
            aggregate_id=command.aggregate_id, events=snapshot_events
        )

    def _create_example(self, command: CreateExample) -> Tuple[Event, ...]:
        return self._repository.create(
            uuid=command.aggregate_id,
            param_one=command.param_one,
            param_two=command.param_two,
        )

    def _update_example(self, command: UpdateExample) -> Tuple[Event, ...]:
        example, seq = self._repository.read(command.aggregate_id)
        events = example.update(
            param_one=command.param_one, param_two=command.param_two
        )
        return self._repository.persist(aggregate_id=command.aggregate_id, events=events)
