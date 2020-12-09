import logging
import os
from typing import TypeVar

from eventz.aggregate import Aggregate
from eventz.protocols import (
    RepositoryProtocol,
    AggregateBuilderProtocol,
    Events,
    EventStoreProtocol,
)

T = TypeVar("T")

log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


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
        log.debug(f"Repository.create with kwargs={kwargs}")
        if "uuid" not in kwargs:
            kwargs["uuid"] = Aggregate.make_id()
            log.debug(f"uuid not found in kwargs. Created as uuid={kwargs['uuid']}")
        events = getattr(self._aggregate_class, "create")(**kwargs)
        log.debug(f"Events obtained from {self._aggregate_class}.create are:")
        log.debug(events)
        log.debug(f"Persisting events to storage with uuid={kwargs['uuid']} ...")
        self._storage.persist(kwargs["uuid"], events)
        log.debug("... events persisted without error.")
        return events

    def read(self, aggregate_id: str) -> T:
        log.debug(f"Repository.read with aggregate_id={aggregate_id}")
        events = self._storage.fetch(aggregate_id=aggregate_id)
        log.debug(f"Events obtained from storage fetch are:")
        log.debug(events)
        return self._builder.create(events)

    def persist(self, aggregate_id: str, events: Events) -> None:
        log.debug(f"Repository.persist with aggregate_id={aggregate_id} and events:")
        log.debug(events)
        log.debug("Persisting to storage ...")
        self._storage.persist(aggregate_id, events)
        log.debug("... events persisted without error.")
