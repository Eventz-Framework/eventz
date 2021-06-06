from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from eventz.commands import ReplayCommand, SnapshotCommand
from eventz.errors import CommandValidationError, UnknownCommandError
from eventz.events import SnapshotEvent
from eventz.messages import Command, Event
from eventz.packets import Packet
from eventz.protocols import MarshallProtocol, ServiceProtocol, RepositoryProtocol, Events


class Service(ABC, ServiceProtocol):
    _standard_commands = (
        "commands.eventz.ReplayCommand",
        "commands.eventz.SnapshotCommand",
    )

    def __init__(self, marshall: MarshallProtocol, repository: RepositoryProtocol):
        self._marshall = marshall
        self._repository: RepositoryProtocol = repository

    @abstractmethod
    def _get_standard_commands(self) -> Tuple[str, ...]:
        """
        Override this function and add additional standard commands for the service
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _process_domain_commands(self, command: Command) -> Events:
        raise NotImplementedError  # pragma: no cover

    def _transform_command_packet(self, command_packet: Packet) -> Command:
        """
        Override this method if you want to use custom logic
        for generating a Command from the incoming Packet
        """
        raise UnknownCommandError

    def domain_command_from_packet(self, command_packet: Packet) -> Command:
        if command_packet.payload["__fqn__"] in (
            self._standard_commands + self._get_standard_commands()
        ):
            payload = self._marshall.transform_keys_deserialisation(command_packet.payload)
            return self._marshall.deserialise_data(payload)
        try:
            return self._transform_command_packet(command_packet)
        except UnknownCommandError:
            err = f"Command `{command_packet.payload['__fqn__']}` is not currently supported."
            raise CommandValidationError(err)
        except Exception as e:
            err = f"Error whilst validating incoming command was: {str(e)}"
            raise CommandValidationError(err)

    def process(self, command: Command) -> Tuple[Event, ...]:
        if isinstance(command, ReplayCommand):
            return self._replay_command(command)
        if isinstance(command, SnapshotCommand):
            return self._snapshot_command(command)
        return self._process_domain_commands(command)

    def _replay_command(self, command: ReplayCommand) -> Tuple[Event, ...]:
        return self._repository.fetch_all_from(
            aggregate_id=command.aggregate_id,
            seq=command.from_seq,
        )

    def _snapshot_command(self, command: SnapshotCommand) -> Tuple[Event, ...]:
        aggregate, seq = self._repository.read(aggregate_id=command.aggregate_id)
        return (
            SnapshotEvent(
                aggregate_id=aggregate.uuid,
                state=self._make_snapshot_state(aggregate),
                order=self._make_snapshot_order(aggregate),
                __seq__=seq,
            ),
        )

    def _make_snapshot_state(self, aggregate) -> Dict:
        """
        Override this method to control exactly how the snapshot state is built
        """
        return {
            k: getattr(aggregate, k)
            for k in self._get_state_params(aggregate)
        }

    def _make_snapshot_order(self, aggregate) -> List[str]:
        """
        Override this method to control the sequence in which
        the snapshot state should be applied
        """
        return self._get_state_params(aggregate)

    def _get_state_params(self, aggregate) -> List[str]:
        return [
            k for k in vars(aggregate).keys() if (not k.startswith("__") and k != "uuid")
        ]
