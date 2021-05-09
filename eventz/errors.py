class AggregateNotFound(Exception):
    pass


class CommandValidationError(Exception):
    pass


class EventValidationError(Exception):
    pass


class EventNotMatchedError(Exception):
    pass


class ServiceNotFoundError(Exception):
    pass


class UnknownCommandError(Exception):
    pass
