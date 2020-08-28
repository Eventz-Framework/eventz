from eventz.aggregate import Aggregate
from tests.example.example_aggregate import ExampleUpdated, ExampleCreated
from tests.example.example_builder import ExampleBuilder

example_id = Aggregate.make_id()
builder = ExampleBuilder()
create_events = [
    ExampleCreated(
        example_id=example_id,
        param_one=123,
        param_two="abc"),
    ExampleUpdated(
        example_id=example_id,
        param_one=321,
        param_two="cba"
    ),
]


def test_builder_creates_an_new_aggregate():
    aggregate = builder.create(create_events)
    assert aggregate.param_one == 321
    assert aggregate.param_two == "cba"


def test_builder_can_update_an_existing_aggregate():
    update_events = [
        ExampleUpdated(
            example_id=example_id,
            param_one=321,
            param_two="def"
        ),
        ExampleUpdated(
            example_id=example_id,
            param_one=321,
            param_two="ghi"
        ),
    ]
    aggregate = builder.create(create_events)
    aggregate = builder.update(aggregate, update_events)
    assert aggregate.param_one == 321
    assert aggregate.param_two == "ghi"
