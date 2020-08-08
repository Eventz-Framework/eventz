from typing import Optional

from eventz.aggregate import Aggregate


class ExampleAggregate(Aggregate):
    def __init__(
            self,
            param_one: int,
            param_two: str = None,
            uuid: Optional[str] = None,
    ):
        super().__init__(uuid)
        self.param_one: int = param_one
        self.param_two: str = param_two
