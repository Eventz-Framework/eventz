import pytest

from eventz.event_bus import EventBus
from eventz.event_bus_default import (
    SubscriptionQueue,
    CollectAllHandler,
    OfTypeHandler,
)
from eventz.messages import Event


class EntityOneEvent(Event):
    def __init__(self, param: str):
        super().__init__()
        self.param = param


class EntityOneCreated(EntityOneEvent):
    version: int = 1


class EntityOneUpdated(EntityOneEvent):
    version: int = 1


class EntityTwoEvent(Event):
    def __init__(self, param: str):
        super().__init__()
        self.param = param


class EntityTwoCreated(EntityTwoEvent):
    version: int = 1


class EntityTwoUpdated(EntityTwoEvent):
    version: int = 1


entity_one_created_event_1 = EntityOneCreated(param="A")
entity_one_created_event_2 = EntityOneCreated(param="B")
entity_one_updated_event_1 = EntityOneUpdated(param="A")
entity_one_updated_event_2 = EntityOneUpdated(param="B")
entity_two_created_event_1 = EntityTwoCreated(param="A")
entity_two_created_event_2 = EntityTwoCreated(param="B")
entity_two_updated_event_1 = EntityTwoUpdated(param="A")
entity_two_updated_event_2 = EntityTwoUpdated(param="B")
all_events = (
    entity_one_created_event_1,
    entity_one_created_event_2,
    entity_one_updated_event_1,
    entity_one_updated_event_2,
    entity_two_created_event_1,
    entity_two_created_event_2,
    entity_two_updated_event_1,
    entity_two_updated_event_2,
)


def test_that_handlers_can_be_registered_and_deregistered():
    subscription_events = []
    EventBus.register_handler(
        "CollectAllEvents1", lambda e: subscription_events.append(e)
    )
    EventBus.register_handler(
        "CollectAllEvents2", lambda e: subscription_events.append(e)
    )
    assert len(EventBus.list_handler_names()) == 2
    EventBus.deregister_handler("CollectAllEvents1")
    assert EventBus.list_handler_names() == ("CollectAllEvents2",)
    EventBus.deregister_handler("CollectAllEvents2")
    assert EventBus.list_handler_names() == tuple()


def test_that_a_handler_cannot_be_created_with_an_existing_name():
    subscription_events1 = []
    EventBus.register_handler(
        "CollectAllEvents", lambda e: subscription_events1.append(e)
    )
    subscription_events2 = []
    with pytest.raises(RuntimeError):
        EventBus.register_handler(
            "CollectAllEvents", lambda e: subscription_events2.append(e)
        )
    EventBus.deregister_handler("CollectAllEvents")
    EventBus.register_handler(
        "CollectAllEvents", lambda e: subscription_events2.append(e)
    )
    assert len(EventBus.list_handler_names()) == 1


def test_that_all_handlers_can_be_cleared():
    subscription_events = []
    EventBus.register_handler(
        "CollectAllEvents1", lambda e: subscription_events.append(e)
    )
    EventBus.register_handler(
        "CollectAllEvents2", lambda e: subscription_events.append(e)
    )
    assert len(EventBus.list_handler_names()) == 2
    EventBus.clear_handlers()
    assert EventBus.list_handler_names() == tuple()


def test_subscription_to_all_events():
    subscription = SubscriptionQueue()
    EventBus.register_handler(
        name="CollectAllEvents", handler=CollectAllHandler(subscription=subscription),
    )
    for event in all_events:
        EventBus.send(event)
    count = 0
    for subscription_event in subscription:
        assert subscription_event == all_events[count]
        count += 1
    assert count == len(all_events)


def test_isinstance_subscription_to_specific_event():
    subscription = SubscriptionQueue()
    EventBus.register_handler(
        name="CollectEntityOneUpdatedEvents",
        handler=OfTypeHandler(subscription=subscription, of_type=EntityOneUpdated),
    )
    for event in all_events:
        EventBus.send(event)
    count = 0
    for subscription_event in subscription:
        assert isinstance(subscription_event, EntityOneUpdated)
        count += 1
    assert count == 2


def test_isinstance_subscription_to_events_by_parent_class():
    subscription = SubscriptionQueue()
    EventBus.register_handler(
        name="CollectEntityOneUpdatedEvents",
        handler=OfTypeHandler(subscription=subscription, of_type=EntityTwoEvent),
    )
    for event in all_events:
        EventBus.send(event)
    count = 0
    for subscription_event in subscription:
        assert isinstance(subscription_event, EntityTwoEvent)
        count += 1
    assert count == 4


def test_all_events_can_be_fetched_from_subscription_in_single_operation():
    subscription = SubscriptionQueue()
    EventBus.register_handler(
        name="CollectEntityOneUpdatedEvents",
        handler=OfTypeHandler(subscription=subscription, of_type=Event),
    )
    for event in all_events:
        EventBus.send(event)
    assert subscription.all() == all_events
