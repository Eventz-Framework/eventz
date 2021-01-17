from eventz.messages import Command


class CreateExample(Command):
    __version__: int = 1

    def __init__(self, aggregate_id: str, param_one: int, param_two: str):
        super().__init__(aggregate_id)
        self.param_one: int = param_one
        self.param_two: str = param_two


class UpdateExample(Command):
    __version__: int = 1

    def __init__(self, aggregate_id: str, param_one: int, param_two: str):
        super().__init__(aggregate_id)
        self.param_one: int = param_one
        self.param_two: str = param_two
