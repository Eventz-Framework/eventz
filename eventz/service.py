from abc import ABC, abstractmethod
from typing import Tuple

from eventz.commands import ReplayCommand, SnapshotCommand
from eventz.messages import Command, Event
from eventz.protocols import ServiceProtocol, RepositoryProtocol, Events


class Service(ABC, ServiceProtocol):
    def __init__(self, repository: RepositoryProtocol):
        self._repository: RepositoryProtocol = repository

    @abstractmethod
    def _process_domain_commands(self, command: Command) -> Events:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _snapshot_command(self, command: SnapshotCommand) -> Events:
        raise NotImplementedError  # pragma: no cover

    def process(self, command: Command) -> Tuple[Event, ...]:
        if isinstance(command, ReplayCommand):
            return self._replay_command(command)
        if isinstance(command, SnapshotCommand):
            return self._snapshot_command(command)
        return self._process_domain_commands(command)

    def transform(self, event: Event) -> Event:
        return event

    def _replay_command(self, command: ReplayCommand) -> Tuple[Event, ...]:
        return self._repository.fetch_all_from(
            aggregate_id=command.aggregate_id,
            seq=command.from_seq,
        )
