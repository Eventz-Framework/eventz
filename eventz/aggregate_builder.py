from abc import ABC, abstractmethod
from typing import Dict, TypeVar

from eventz.aggregate import Aggregate
from eventz.messages import Event
from eventz.protocols import AggregateBuilderProtocol, Events

T = TypeVar("T")


class AggregateBuilder(ABC, AggregateBuilderProtocol):
    def create(self, events: Events) -> T:
        kwargs = {}
        return self._apply_events(kwargs, events)

    def update(self, aggregate: Aggregate, events: Events) -> T:
        kwargs = vars(aggregate)
        return self._apply_events(kwargs, events)

    def _apply_events(self, kwargs: Dict, events: Events) -> T:
        for event in events:
            kwargs = self._apply_event(kwargs, event)
        return self._new_aggregate(kwargs)

    @abstractmethod
    def _apply_event(self, kwargs: Dict, event: Event) -> Dict:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def _new_aggregate(self, kwargs: Dict) -> T:  # pragma: no cover
        """
        i.e.: return MyAggregate(**kwargs)
        """
        raise NotImplementedError
