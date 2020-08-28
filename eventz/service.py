from abc import ABC, abstractmethod

from eventz.messages import Command
from eventz.protocols import ProcessesCommandsProtocol, RepositoryProtocol, Events


class Service(ABC, ProcessesCommandsProtocol):
    def __init__(self, repository: RepositoryProtocol):
        self._repository: RepositoryProtocol = repository

    @abstractmethod
    def process(self, command: Command) -> Events:
        raise NotImplementedError  # pragma: no cover
