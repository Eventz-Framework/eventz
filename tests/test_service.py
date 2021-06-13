import pytest

from eventz.aggregate import Aggregate
from eventz.commands import ReplayCommand, SnapshotCommand
from eventz.dummy_storage import DummyStorage
from eventz.events import SnapshotEvent
from eventz.marshall import FqnResolver, Marshall
from eventz.packets import Packet
from eventz.repository import Repository
from tests.example.commands import CreateExample, UpdateExample
from tests.example.example_aggregate import (
    ExampleCreated,
    ExampleAggregate,
    ExampleUpdated,
)
from tests.example.example_builder import ExampleBuilder
from tests.example.example_service import ExampleService

example_id = Aggregate.make_id()
example_created_event = ExampleCreated(
    aggregate_id=example_id, param_one=123, param_two="abc"
)
example_updated_event = ExampleUpdated(
    aggregate_id=example_id, param_one=321, param_two="cba"
)


def test_service_processes_create_command():
    repository = Repository(
        aggregate_class=ExampleAggregate,
        storage=DummyStorage(),
        builder=ExampleBuilder(),
    )
    resolver = FqnResolver(fqn_map={
        "commands.eventz.*": "eventz.commands.*",
    })
    marshall = Marshall(fqn_resolver=resolver)
    service = ExampleService(marshall=marshall, repository=repository)
    command = CreateExample(aggregate_id=example_id, param_one=123, param_two="abc")
    events = service.process(command)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ExampleCreated)
    assert event.aggregate_id == example_id
    assert event.param_one == 123
    assert event.param_two == "abc"


def test_service_processes_update_command():
    # set up the events that have already taken place
    initial_events = (
        ExampleCreated(aggregate_id=example_id, param_one=123, param_two="abc"),
    )
    storage = DummyStorage()
    builder = ExampleBuilder()
    storage.persist(aggregate_id=example_id, events=initial_events)
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=storage, builder=builder,
    )
    resolver = FqnResolver(fqn_map={
        "commands.eventz.*": "eventz.commands.*",
    })
    marshall = Marshall(fqn_resolver=resolver)
    service = ExampleService(marshall=marshall, repository=repository)
    command = UpdateExample(aggregate_id=example_id, param_one=321, param_two="cba")
    events = service.process(command)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ExampleUpdated)
    assert event.aggregate_id == example_id
    assert event.param_one == 321
    assert event.param_two == "cba"
    all_events = storage.fetch(example_id)
    assert len(all_events) == 2
    assert isinstance(all_events[0], ExampleCreated)
    assert isinstance(all_events[1], ExampleUpdated)
    example: ExampleAggregate = builder.create(all_events)
    assert example.uuid == example_id
    assert example.param_one == 321
    assert example.param_two == "cba"


@pytest.mark.parametrize(
    "from_seq,expected_events",
    [
        (1, (example_created_event.sequence(1), example_updated_event.sequence(2),),),
        (2, (example_updated_event.sequence(2),)),
    ],
)
def test_service_processes_replay_command(from_seq, expected_events):
    # set up the events that have already taken place
    initial_events = (
        example_created_event,
        example_updated_event,
    )
    storage = DummyStorage()
    builder = ExampleBuilder()
    storage.persist(aggregate_id=example_id, events=initial_events)
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=storage, builder=builder,
    )
    resolver = FqnResolver(fqn_map={
        "commands.eventz.*": "eventz.commands.*",
    })
    marshall = Marshall(fqn_resolver=resolver)
    service = ExampleService(marshall=marshall, repository=repository)
    command = ReplayCommand(aggregate_id=example_id, from_seq=from_seq)
    assert service.process(command) == expected_events


def test_service_processes_snapshot_command():
    initial_events = (
        example_created_event,
        example_updated_event,
    )
    storage = DummyStorage()
    builder = ExampleBuilder()
    storage.persist(aggregate_id=example_id, events=initial_events)
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=storage, builder=builder,
    )
    resolver = FqnResolver(fqn_map={
        "commands.eventz.*": "eventz.commands.*",
    })
    marshall = Marshall(fqn_resolver=resolver)
    service = ExampleService(marshall=marshall, repository=repository)
    command = SnapshotCommand(aggregate_id=example_id)
    events = service.process(command)
    assert len(events) == 1
    snapshot_event = events[0]
    assert isinstance(snapshot_event, SnapshotEvent)
    # the __seq__ of the snapshot event should match that of the latest event
    assert snapshot_event.__seq__ == 2
    assert snapshot_event.aggregate_id == example_id
    assert snapshot_event.state["param_one"] == 321
    assert snapshot_event.state["param_two"] == "cba"
    assert snapshot_event.order == ["param_one", "param_two"]
    # the snapshot event itself should not be persisted
    assert len(storage.persisted_events[example_id]) == 2


def test_domain_command_from_packet():
    aggregate_id = Aggregate.make_id()
    dialog_id = Aggregate.make_id()
    unicast_command_packet = Packet(
        subscribers=["aaaaaa"],
        message_type="COMMAND",
        route="ExampleService",
        msgid=aggregate_id,
        dialog=dialog_id,
        seq=1,
        payload={
            "__fqn__": "commands.eventz.ReplayCommand",
            "__version__": 1,
            "__msgid__": "203cea3c-1815-47cd-b2d3-7a7f29854df7",
            "__timestamp__": "2021-05-03T17:32:44.404Z",
            "aggregateId": aggregate_id,
        },
    )
    fqn_map = {
        "commands.eventz.*": "eventz.commands.*",
    }
    marshall = Marshall(fqn_resolver=FqnResolver(fqn_map=fqn_map))
    repository = Repository(
        aggregate_class=ExampleAggregate,
        storage=DummyStorage(),
        builder=ExampleBuilder(),
    )
    service = ExampleService(marshall=marshall, repository=repository)
    domain_command = service.domain_command_from_packet(unicast_command_packet)
    assert isinstance(domain_command, ReplayCommand)
