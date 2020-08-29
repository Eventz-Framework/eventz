from typing import TypeVar

from eventz.aggregate import Aggregate
from eventz.protocols import (
    RepositoryProtocol,
    AggregateBuilderProtocol,
    Events,
    EventStoreProtocol,
)

T = TypeVar("T")


class Repository(RepositoryProtocol[T]):
    def __init__(
        self,
        aggregate_class: type,
        storage: EventStoreProtocol,
        builder: AggregateBuilderProtocol,
    ):
        self._aggregate_class: type = aggregate_class
        self._storage: EventStoreProtocol = storage
        self._builder: AggregateBuilderProtocol = builder

    def create(self, **kwargs) -> Events:
        if "uuid" not in kwargs:
            kwargs["uuid"] = Aggregate.make_id()
        events = getattr(self._aggregate_class, "create")(**kwargs)
        self._storage.persist(kwargs["uuid"], events)
        return events

    def read(self, aggregate_id: str) -> T:
        events = self._storage.fetch(aggregate_id=aggregate_id)
        return self._builder.create(events)

    def persist(self, aggregate_id: str, events: Events) -> None:
        self._storage.persist(aggregate_id, events)
