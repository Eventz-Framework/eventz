from unittest.mock import patch

from eventz.aggregate import Aggregate
from eventz.packet_manager import PacketManager
from eventz.packets import Packet
from tests.example.example_aggregate import ExampleCreated, ExampleUpdated

aggregate_id = Aggregate.make_id()
command_msgid = Aggregate.make_id()
dialog_id = Aggregate.make_id()
payload_msg_id = Aggregate.make_id()
broadcast_command_packet = Packet(
    subscribers=("aaaaaa",),
    message_type="COMMAND",
    route="ExampleService",
    msgid=command_msgid,
    dialog=dialog_id,
    seq=1,
    payload={
        "__fqn__": "commands.example.CreateExample",
        "__version__": 1,
        "__msgid__": payload_msg_id,
        "__timestamp__": "2021-05-03T17:32:44.404Z",
        "aggregateId": aggregate_id,
        "paramOne": 1,
        "paramTwo": "abc",
    }
)
unicast_command_packet = Packet(
    subscribers=("aaaaaa",),
    message_type="COMMAND",
    route="ExampleService",
    msgid=command_msgid,
    dialog=dialog_id,
    seq=1,
    payload={
        "__fqn__": "commands.eventz.ReplayCommand",
        "__version__": 1,
        "__msgid__": payload_msg_id,
        "__timestamp__": "2021-05-03T17:32:44.404Z",
        "aggregateId": aggregate_id,
    }
)


def test_get_broadcast_command_packet():
    packet_manager = PacketManager()
    packet_manager.init_dialog(
        unicast_command_packet,
        ("bbbbbb", "cccccc",)
    )
    assert packet_manager.get_broadcast_command_packet() is None
    packet_manager = PacketManager()
    packet_manager.init_dialog(
        broadcast_command_packet,
        ("bbbbbb", "cccccc",)
    )
    assert packet_manager.get_broadcast_command_packet() == Packet(
        subscribers=("bbbbbb", "cccccc",),
        message_type="COMMAND",
        route="ExampleService",
        msgid=command_msgid,
        dialog=dialog_id,
        seq=1,
        payload={
            "__fqn__": "commands.example.CreateExample",
            "__version__": 1,
            "__msgid__": payload_msg_id,
            "__timestamp__": "2021-05-03T17:32:44.404Z",
            "aggregateId": aggregate_id,
            "paramOne": 1,
            "paramTwo": "abc",
        }
    )


@patch("eventz.entity.uuid4")
def test_get_ack_packet(mock_uuid4):
    new_msg_id = "741e00f2-85c3-4c9f-9d38-886711579c34"
    mock_uuid4.return_value = new_msg_id
    packet_manager = PacketManager()
    packet_manager.init_dialog(
        broadcast_command_packet,
        ("bbbbbb", "cccccc",)
    )
    assert packet_manager.get_ack_packet() == Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="ACK",
        route="ExampleService",
        msgid=new_msg_id,
        dialog=dialog_id,
        seq=2,
        payload=None,
    )


@patch("eventz.entity.uuid4")
def test_get_next_event_packet(mock_uuid4):
    new_msg_id = "741e00f2-85c3-4c9f-9d38-886711579c34"
    mock_uuid4.return_value = new_msg_id
    packet_manager = PacketManager()
    packet_manager.init_dialog(
        broadcast_command_packet,
        ("bbbbbb", "cccccc",)
    )
    event1 = Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="EVENT",
        route="ExampleService",
        msgid=Aggregate.make_id(),
        dialog=dialog_id,
        seq=3,
        payload=ExampleCreated(
            aggregate_id=command_msgid, param_one=123, param_two="abc"
        ),
    )
    event2 = Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="EVENT",
        route="ExampleService",
        msgid=Aggregate.make_id(),
        dialog=dialog_id,
        seq=4,
        payload=ExampleUpdated(
            aggregate_id=command_msgid, param_one=321, param_two="cba"
        ),
    )
    next_event = ExampleUpdated(
        aggregate_id=command_msgid,
        param_one=111,
        param_two="aaa",
    )
    assert packet_manager.get_next_event_packet(
        event=next_event, event_packets_sent=[event1, event2]
    ) == Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="EVENT",
        route="ExampleService",
        msgid=new_msg_id,
        dialog=dialog_id,
        seq=5,
        payload=next_event,
    )


@patch("eventz.entity.uuid4")
def test_get_done_event_packet(mock_uuid4):
    event_msgid = "203cea3c-1815-47cd-b2d3-7a7f29854df7"
    new_msg_id = "741e00f2-85c3-4c9f-9d38-886711579c34"
    mock_uuid4.return_value = new_msg_id
    packet_manager = PacketManager()
    packet_manager.init_dialog(
        broadcast_command_packet,
        ("bbbbbb", "cccccc",)
    )
    event1 = Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="EVENT",
        route="ExampleService",
        msgid=event_msgid,
        dialog=dialog_id,
        seq=3,
        payload=ExampleCreated(
            aggregate_id=command_msgid, param_one=123, param_two="abc"
        ),
    )
    assert packet_manager.get_done_event_packet(
        event_packets_sent=[event1]
    ) == Packet(
        subscribers=("aaaaaa", "bbbbbb", "cccccc",),
        message_type="DONE",
        route="ExampleService",
        msgid=new_msg_id,
        dialog=dialog_id,
        seq=4,
        payload=(event_msgid,),
    )
