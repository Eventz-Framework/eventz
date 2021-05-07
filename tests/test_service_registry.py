import pytest

from eventz.dummy_storage import DummyStorage
from eventz.errors import ServiceNotFoundError
from eventz.marshall import FqnResolver, Marshall
from eventz.repository import Repository
from eventz.service_registry import ServiceRegistry
from tests.example.example_aggregate import ExampleAggregate
from tests.example.example_builder import ExampleBuilder
from tests.example.example_service import ExampleService


def test_correct_service_is_returned_from_message():
    builder = ExampleBuilder()
    repository = Repository(
        aggregate_class=ExampleAggregate, storage=DummyStorage(), builder=builder,
    )
    fqn_map = {
        "commands.eventz.*": "eventz.commands.*",
    }
    marshall = Marshall(fqn_resolver=FqnResolver(fqn_map=fqn_map))
    example_service = ExampleService(marshall=marshall, repository=repository)
    service_registry = ServiceRegistry()
    service_registry.register("ExampleService", service=example_service)
    with pytest.raises(ServiceNotFoundError):
        service_registry.get_service("OtherService")
    assert isinstance(service_registry.get_service("ExampleService"), ExampleService)
