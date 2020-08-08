from eventz.aggregate import Aggregate
from tests.example.example_aggregate import ExampleAggregate


def test_aggregate_can_generate_a_uuid():
    uuid = Aggregate.make_id()
    assert isinstance(uuid, str)


def test_aggregate_can_be_created_with_a_uuid():
    uuid = Aggregate.make_id()
    aggregate = ExampleAggregate(param_one=1, param_two="abc", uuid=uuid)
    assert isinstance(aggregate.uuid, str)


def test_aggregate_can_be_created_without_a_uuid():
    aggregate = ExampleAggregate(param_one=1, param_two="abc")
    assert isinstance(aggregate.uuid, str)
