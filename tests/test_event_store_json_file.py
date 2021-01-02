import json
import os
from pathlib import Path

from eventz.event_store_json_file import EventStoreJsonFile
from eventz.marshall import Marshall, FqnResolver
from eventz.codecs.datetime import Datetime
from tests.conftest import parent_id1

marshall = Marshall(
    fqn_resolver=FqnResolver(
        fqn_map={
            "tests.Child": "tests.example.child.Child",
            "tests.Children": "tests.example.children.Children",
            "tests.ParentCreated": "tests.example.parent.ParentCreated",
            "tests.ChildChosen": "tests.example.parent.ChildChosen",
        }
    ),
    codecs={"codecs.eventz.Datetime": Datetime()},
)


def test_sequence_of_events_can_be_read(
    json_events, parent_created_event, child_chosen_event
):
    # set up the store
    storage_path = str(Path(__file__).absolute().parent) + "/storage"
    store = EventStoreJsonFile(
        storage_path=storage_path, marshall=marshall, recreate_storage=True,
    )
    # insert fixture data into the storage
    if not os.path.isdir(storage_path):
        os.mkdir(storage_path)
        os.chmod(storage_path, 0o777)
    with open(f"{storage_path}/{parent_id1}.json", "w+") as json_file:
        json.dump(json_events, json_file)
    # run test and make assertion
    events = store.fetch(parent_id1)
    assert events == (parent_created_event.sequence(1), child_chosen_event.sequence(2))


def test_new_sequence_of_events_can_be_persisted(
    json_events, parent_created_event, child_chosen_event
):
    storage_path = str(Path(__file__).absolute().parent) + "/storage"
    store = EventStoreJsonFile(
        storage_path=storage_path, marshall=marshall, recreate_storage=True,
    )
    assert store.fetch(parent_id1) == ()
    store.persist(parent_id1, (parent_created_event, child_chosen_event,))
    with open(f"{storage_path}/{parent_id1}.json", "r+") as json_file:
        assert json_file.read() == (
            '[{"__fqn__":"tests.ParentCreated","__msgid__":"11111111-1111-1111-1111-111111111111",'
            '"__seq__":1,"__timestamp__":{"__codec__":"codecs.eventz.Datetime","params":'
            '{"timestamp":"2020-01-02T03:04:05.123Z"}},"__version__":1,"children":'
            '{"__fqn__":"tests.Children","items":[{"__fqn__":"tests.Child","name":"Child '
            'One"},{"__fqn__":"tests.Child","name":"Child '
            'Two"},{"__fqn__":"tests.Child","name":"Child Three"}],"name":"Group '
            f'One"}},"parentId":"{parent_id1}"}},'
            '{"__fqn__":"tests.ChildChosen","__msgid__":"22222222-2222-2222-2222-222222222222",'
            '"__seq__":2,"__timestamp__":{"__codec__":"codecs.eventz.Datetime","params":'
            '{"timestamp":"2020-01-02T03:04:06.123Z"}},"__version__":1,'
            '"child":{"__fqn__":"tests.Child","name":"Child '
            f'Three"}},"parentId":"{parent_id1}"}}]'
        )
