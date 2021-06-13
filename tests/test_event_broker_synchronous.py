from unittest.mock import patch

from freezegun import freeze_time

from eventz.packets import Packet
from tests.example.example_aggregate import ExampleCreated


@freeze_time("2021-08-31")
@patch("eventz.entity.uuid4")
def test_default_flow_success(mock_uuid4, event_broker_synchronous):
    aggregate_id = "a1b2c3"
    payload_msg_id_command = "999999"
    payload_msg_id_created_event = "888888"
    dialog_id = msgid1 = "111111"
    msgid2 = "222222"
    msgid3 = "333333"
    msgid4 = "444444"
    msgid5 = "555555"
    msgid6 = "666666"
    mock_uuid4.side_effect = (msgid2, payload_msg_id_created_event, msgid3, msgid4, msgid5, msgid6,)
    incoming_command_packet = Packet(
        subscribers=("aaaaaa",),
        message_type="COMMAND",
        route="ExampleService",
        msgid=msgid1,
        dialog=dialog_id,
        seq=1,
        payload={
            "__fqn__": "commands.example.CreateExample",
            "__version__": 1,
            "__msgid__": payload_msg_id_command,
            "__timestamp__": "2021-05-03T17:32:44.404Z",
            "aggregateId": aggregate_id,
            "paramOne": 1,
            "paramTwo": "abc",
        }
    )
    event_broker_synchronous.handle(command_packet=incoming_command_packet)
    publisher_dummy = event_broker_synchronous.get_publisher("Dummy")
    assert len(publisher_dummy.published_packets) == 3  # ACK, EVENT, DONE
    assert publisher_dummy.published_packets[0] == Packet(
        subscribers=("aaaaaa",),
        message_type="ACK",
        route="ExampleService",
        msgid=msgid2,
        dialog=dialog_id,
        seq=2,
        payload=None,
    )
    assert publisher_dummy.published_packets[1] == Packet(
        subscribers=("aaaaaa",),
        message_type="EVENT",
        route="ExampleService",
        msgid=msgid3,
        dialog=dialog_id,
        seq=3,
        payload=ExampleCreated(
            aggregate_id=aggregate_id,
            param_one=1,
            param_two="abc",
            __msgid__=payload_msg_id_created_event,
            __seq__=1,
        ),
    )
    assert publisher_dummy.published_packets[2] == Packet(
        subscribers=("aaaaaa",),
        message_type="DONE",
        route="ExampleService",
        msgid=msgid4,
        dialog=dialog_id,
        seq=4,
        payload=(msgid3,),
    )
