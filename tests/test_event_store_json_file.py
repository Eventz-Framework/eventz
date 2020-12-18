import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from eventz.entity import Entity
from eventz.event_store_json_file import EventStoreJsonFile
from eventz.marshall import Marshall, FqnResolver
from eventz.codecs.datetime import Datetime
from tests.example.child import Child
from tests.example.children import Children
from tests.example.parent import ParentCreated, ChildChosen

parent_id1 = Entity.make_id()
msgid1 = "11111111-1111-1111-1111-111111111111"
msgid2 = "22222222-2222-2222-2222-222222222222"
dt_iso1 = "2020-01-02T03:04:05.123456"
dt_iso2 = "2020-01-02T03:04:06.123456"
dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
dt2 = datetime(2020, 1, 2, 3, 4, 6, 123456)
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
    assert events == (parent_created_event, child_chosen_event)


def test_new_sequence_of_events_can_be_persisted(
    json_events, parent_created_event, child_chosen_event
):
    storage_path = str(Path(__file__).absolute().parent) + "/storage"
    store = EventStoreJsonFile(
        storage_path=storage_path, marshall=marshall, recreate_storage=True,
    )
    assert store.fetch(parent_id1) == ()
    store.persist(parent_id1, [parent_created_event, child_chosen_event])
    with open(f"{storage_path}/{parent_id1}.json", "r+") as json_file:
        assert json_file.read() == (
            '[{"__fqn__":"tests.ParentCreated","__msgid__":"11111111-1111-1111-1111-111111111111",'
            '"__timestamp__":{"__codec__":"codecs.eventz.Datetime","params":'
            '{"timestamp":"2020-01-02T03:04:05.123Z"}},"__version__":1,"children":'
            '{"__fqn__":"tests.Children","items":[{"__fqn__":"tests.Child","name":"Child '
            'One"},{"__fqn__":"tests.Child","name":"Child '
            'Two"},{"__fqn__":"tests.Child","name":"Child Three"}],"name":"Group '
            f'One"}},"parentId":"{parent_id1}"}},'
            '{"__fqn__":"tests.ChildChosen","__msgid__":"22222222-2222-2222-2222-222222222222",'
            '"__timestamp__":{"__codec__":"codecs.eventz.Datetime","params":'
            '{"timestamp":"2020-01-02T03:04:06.123Z"}},"__version__":1,'
            '"child":{"__fqn__":"tests.Child","name":"Child '
            f'Three"}},"parentId":"{parent_id1}"}}]'
        )


@pytest.fixture
def parent_created_event():
    return ParentCreated(
        parent_id=parent_id1,
        children=Children(
            name="Group One",
            items=[
                Child(name="Child One"),
                Child(name="Child Two"),
                Child(name="Child Three"),
            ],
        ),
        __msgid__=msgid1,
        __timestamp__=dt1,
    )


@pytest.fixture
def child_chosen_event():
    return ChildChosen(
        parent_id=parent_id1,
        child=Child(name="Child Three"),
        __msgid__=msgid2,
        __timestamp__=dt2,
    )


@pytest.fixture()
def json_events():
    return [
        {
            "__fqn__": "tests.ParentCreated",
            "__version__": 1,
            "__msgid__": msgid1,
            "__timestamp__": {
                "__codec__": "codecs.eventz.Datetime",
                "params": {"timestamp": dt_iso1},
            },
            "parent_id": parent_id1,
            "children": {
                "__fqn__": "tests.Children",
                "name": "Group One",
                "items": [
                    {"__fqn__": "tests.Child", "name": "Child One",},
                    {"__fqn__": "tests.Child", "name": "Child Two",},
                    {"__fqn__": "tests.Child", "name": "Child Three",},
                ],
            },
        },
        {
            "__fqn__": "tests.ChildChosen",
            "__version__": 1,
            "__msgid__": msgid2,
            "__timestamp__": {
                "__codec__": "codecs.eventz.Datetime",
                "params": {"timestamp": dt_iso2},
            },
            "parent_id": parent_id1,
            "child": {"__fqn__": "tests.Child", "name": "Child Three",},
        },
    ]
