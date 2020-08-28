from eventz.messages import Command


class CreateExample(Command):
    version: int = 1

    def __init__(self, example_id: str, param_one: int, param_two: str):
        super().__init__()
        self.example_id: str = example_id
        self.param_one: int = param_one
        self.param_two: str = param_two


class UpdateExample(Command):
    version: int = 1

    def __init__(self, example_id: str, param_one: int, param_two: str):
        super().__init__()
        self.example_id: str = example_id
        self.param_one: int = param_one
        self.param_two: str = param_two
