import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, TypeVar

from eventz.aggregate import Aggregate
from eventz.messages import Event
from eventz.protocols import AggregateBuilderProtocol, Events

T = TypeVar("T")

log = logging.getLogger(__name__)
log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


class AggregateBuilder(ABC, AggregateBuilderProtocol):
    def create(self, events: Events) -> T:
        log.debug("AggregateBuilder.create")
        kwargs = {}
        return self._apply_events(kwargs, events)

    def update(self, aggregate: Aggregate, events: Events) -> T:
        log.debug("AggregateBuilder.update")
        kwargs = vars(aggregate)
        return self._apply_events(kwargs, events)

    def _apply_events(self, kwargs: Dict, events: Events) -> T:
        log.debug(f"AggregateBuilder._apply_events with initial kwargs={kwargs}")
        for event in events:
            log.debug(f"... Event: {event}")
            kwargs = self._apply_event(kwargs, event)
            log.debug(f"... Updated kwargs: {kwargs}")
        log.debug("Creating new aggregate with kwargs.")
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
