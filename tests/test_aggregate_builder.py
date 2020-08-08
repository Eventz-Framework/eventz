from tests.example.events import ExampleUpdated, ExampleCreated
from tests.example.example_builder import ExampleBuilder

builder = ExampleBuilder()
create_events = [
    ExampleCreated(param_one=1),
    ExampleUpdated(param_two="abc"),
]


def test_builder_creates_an_new_aggregate():
    aggregate = builder.create(create_events)
    assert aggregate.param_one == 1
    assert aggregate.param_two == "abc"


def test_builder_can_update_an_existing_aggregate():
    update_events = [
        ExampleUpdated(param_two="def"),
        ExampleUpdated(param_two="ghi"),
    ]
    aggregate = builder.create(create_events)
    aggregate = builder.update(aggregate, update_events)
    assert aggregate.param_one == 1
    assert aggregate.param_two == "ghi"
