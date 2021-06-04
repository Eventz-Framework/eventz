import logging
import os
from typing import Optional, Tuple, TypeVar

from eventz.aggregate import Aggregate
from eventz.protocols import (
    RepositoryProtocol,
    AggregateBuilderProtocol,
    Events,
    EventStoreProtocol,
)

T = TypeVar("T")

log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))


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
        log.info(f"Repository.create with kwargs={kwargs}")
        if "uuid" not in kwargs:
            kwargs["uuid"] = Aggregate.make_id()
            log.info(f"uuid not found in kwargs. Created as uuid={kwargs['uuid']}")
        events = getattr(self._aggregate_class, "create")(**kwargs)
        log.info(f"{len(events)} events obtained from {self._aggregate_class}.create are:")
        log.info(events)
        log.info(f"Persisting events to storage with uuid={kwargs['uuid']} ...")
        events = self._storage.persist(kwargs["uuid"], events)
        log.info("... events persisted without error.")
        return events

    def read(self, aggregate_id: str) -> Tuple[T, int]:
        """
        Returns a Tuple consisting of the latest build of the aggregate and the
        __seq__ of the last event (i.e. the __seq__ of the aggregate snapshot)
        """
        log.info(f"Repository.read with aggregate_id={aggregate_id}")
        events = self._storage.fetch(aggregate_id=aggregate_id)
        log.info(f"{len(events)} events obtained from storage fetch are:")
        log.info(events)
        return self._builder.create(events), self._get_highest_sequence(events)

    def _get_highest_sequence(self, events: Events) -> int:
        if len(events) == 0:
            return 0
        return events[-1].__seq__

    def persist(self, aggregate_id: str, events: Events) -> Events:
        log.info(f"Repository.persist with aggregate_id={aggregate_id} and {len(events)} events:")
        log.info(events)
        log.info("Persisting to storage ...")
        events = self._storage.persist(aggregate_id, events)
        log.info("... events persisted without error.")
        return events

    def fetch_all_from(self, aggregate_id: str, seq: Optional[int] = None) -> Events:
        """
        :param aggregate_id:
        :param seq: Optional sequence number from where in history events should be returned @TODO
        """
        log.info(
            f"Repository.fetch_all_from with aggregate_id={aggregate_id} and seq={seq}"
        )
        events = self._storage.fetch(aggregate_id=aggregate_id, seq=seq)
        log.info(f"{len(events)} events obtained from storage fetch are:")
        log.info(events)
        return events

    def get_builder(self) -> AggregateBuilderProtocol:
        return self._builder
