from eventz.event_bus import EventBus
from eventz.repository import Repository
from tests.example.dummy_storage import DummyStorage
from tests.example.events import ExampleEvent
from tests.example.example_builder import ExampleBuilder
from tests.example.example_aggregate import ExampleAggregate


def test_that_handler_is_named_after_the_repositories_aggregate():
    repository = Repository(
        aggregate_class=ExampleAggregate,
        aggregate_event=ExampleEvent,
        storage=DummyStorage(),
        builder=ExampleBuilder(),
    )
    assert "RepositoryCollectExampleAggregateEvents" in EventBus.list_handler_names()
