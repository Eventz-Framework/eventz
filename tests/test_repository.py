from eventz.dummy_storage import DummyStorage
from eventz.repository import Repository
from tests.conftest import parent_id1
from tests.example.example_aggregate import ExampleAggregate
from tests.example.example_builder import ExampleBuilder


def test_create():
    builder = ExampleBuilder()
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=DummyStorage(), builder=builder,
    )
    events = repository.create(param_one=123, param_two="abc")
    example = builder.create(events)
    assert example.param_one == 123
    assert example.param_two == "abc"


def test_fetch_all_events(parent_created_event, child_chosen_event):
    storage = DummyStorage()
    storage.persist(parent_id1, (parent_created_event, child_chosen_event,))
    builder = ExampleBuilder()
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=storage, builder=builder,
    )
    events = repository.fetch_all_from(aggregate_id=parent_id1)
    assert events == (parent_created_event, child_chosen_event,)
