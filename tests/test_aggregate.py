from eventz.aggregate import Aggregate
from tests.example.example_aggregate import ExampleAggregate


def test_aggregate_can_generate_a_uuid():
    uuid = Aggregate.make_id()
    assert isinstance(uuid, str)


def test_aggregate_creation():
    uuid = Aggregate.make_id()
    aggregate = ExampleAggregate(uuid=uuid, param_one=1, param_two="abc")
    assert aggregate.uuid == uuid
