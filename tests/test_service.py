from eventz.aggregate import Aggregate
from eventz.dummy_storage import DummyStorage
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


def test_service_processes_create_command():
    repository = Repository(
        aggregate_class=ExampleAggregate,
        storage=DummyStorage(),
        builder=ExampleBuilder(),
    )
    service = ExampleService(repository)
    command = CreateExample(example_id=example_id, param_one=123, param_two="abc")
    events = service.process(command)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ExampleCreated)
    assert event.example_id == example_id
    assert event.param_one == 123
    assert event.param_two == "abc"


def test_service_processes_update_command():
    # set up the events that have already taken place
    initial_events = (
        ExampleCreated(example_id=example_id, param_one=123, param_two="abc"),
    )
    storage = DummyStorage()
    builder = ExampleBuilder()
    storage.persist(aggregate_id=example_id, events=initial_events)
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=storage, builder=builder,
    )
    service = ExampleService(repository)
    command = UpdateExample(example_id=example_id, param_one=321, param_two="cba")
    events = service.process(command)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, ExampleUpdated)
    assert event.example_id == example_id
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
