from eventz.dummy_storage import DummyStorage
from eventz.repository import Repository
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
