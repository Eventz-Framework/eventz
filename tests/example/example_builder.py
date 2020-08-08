from typing import Dict

from eventz.aggregate_builder import AggregateBuilder
from eventz.errors import EventNotMatchedError
from eventz.messages import Event
from tests.example.events import ExampleCreated, ExampleUpdated
from tests.example.example_aggregate import ExampleAggregate


class ExampleBuilder(AggregateBuilder):
    def _apply_event(self, kwargs: Dict, event: Event) -> Dict:
        if isinstance(event, ExampleCreated):
            kwargs["param_one"] = event.param_one
            return kwargs
        if isinstance(event, ExampleUpdated):
            kwargs["param_two"] = event.param_two
            return kwargs
        raise EventNotMatchedError(f"Could not match even '{str(type(event))}'.")

    def _new_aggregate(self, kwargs: Dict) -> ExampleAggregate:
        return ExampleAggregate(**kwargs)
