from typing import Dict, Sequence

from eventz.aggregate import Aggregate
from eventz.event_bus import EventBus
from eventz.event_bus_default import SubscriptionQueue, OfTypeHandler
from eventz.event_store.event_store_protocol import EventStoreProtocol
from eventz.messages import Event
from eventz.protocols import RepositoryProtocol, AggregateBuilderProtocol


class Repository(RepositoryProtocol):
    def __init__(
        self,
        aggregate_class: type,
        aggregate_event: type,
        storage: EventStoreProtocol,
        builder: AggregateBuilderProtocol,
    ):
        self._aggregate_class: type = aggregate_class
        self._aggregate_event: type = aggregate_event
        self._storage: EventStoreProtocol = storage
        self._builder: AggregateBuilderProtocol = builder
        self._event_subscription: SubscriptionQueue = SubscriptionQueue()
        EventBus.register_handler(
            name=f"RepositoryCollect{self._aggregate_class.__name__}Events",
            handler=OfTypeHandler(
                subscription=self._event_subscription, of_type=self._aggregate_event,
            ),
        )

    def create(self, **kwargs: Dict) -> Aggregate:
        aggregate = getattr(self._aggregate_class, "create")(**kwargs)
        events = self._event_subscription.all()
        self._storage.persist(events)
        return aggregate

    def read(self, aggregate_id: str) -> Aggregate:
        events = self._storage.fetch(aggregate_id=aggregate_id)
        return self._builder.create(events)

    def persist(self, aggregate_id: str, events: Sequence[Event]):
        self._storage.persist(aggregate_id, events)
