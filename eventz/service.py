from collections import Iterable

from eventz.protocols import ProcessesCommandsProtocol
from eventz.messages import Event, Command


class Service(ProcessesCommandsProtocol):
    def process(self, command: Command) -> Iterable[Event]:
        ...
