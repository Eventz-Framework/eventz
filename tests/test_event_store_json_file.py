import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from eventz.entity import Entity
from eventz.event_store_json_file import EventStoreJsonFile
from eventz.marshall import Marshall, DatetimeCodec
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


def test_sequence_of_events_can_be_read(
    json_events, parent_created_event, child_chosen_event
):
    # set up the store
    storage_path = str(Path(__file__).absolute().parent) + "/storage"
    store = EventStoreJsonFile(
        storage_path=storage_path,
        marshall=Marshall({"eventz.marshall.DatetimeCodec": DatetimeCodec()}),
        recreate_storage=True,
    )
    # insert fixture data into the storage
    if not os.path.isdir(storage_path):
        os.mkdir(storage_path)
        os.chmod(storage_path, 0o777)
    with open(f"{storage_path}/{parent_id1}.json", "w+") as json_file:
        json.dump(json_events, json_file)
    # run test and make assertion
    assert store.fetch(parent_id1) == (parent_created_event, child_chosen_event)


def test_new_sequence_of_events_can_be_persisted(
    json_events, parent_created_event, child_chosen_event
):
    storage_path = str(Path(__file__).absolute().parent) + "/storage"
    store = EventStoreJsonFile(
        storage_path=storage_path,
        marshall=Marshall({"eventz.marshall.DatetimeCodec": DatetimeCodec()}),
        recreate_storage=True,
    )
    assert store.fetch(parent_id1) == ()
    store.persist(parent_id1, [parent_created_event, child_chosen_event])
    with open(f"{storage_path}/{parent_id1}.json", "r+") as json_file:
        persisted_json = json.load(json_file)
        assert persisted_json == json.dumps(json_events, sort_keys=True)


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
        msgid=msgid1,
        timestamp=dt1,
    )


@pytest.fixture
def child_chosen_event():
    return ChildChosen(
        parent_id=parent_id1,
        child=Child(name="Child Three"),
        msgid=msgid2,
        timestamp=dt2,
    )


@pytest.fixture()
def json_events():
    return [
        {
            "__fcn__": "tests.example.parent.ParentCreated",
            "__version__": 1,
            "msgid": msgid1,
            "timestamp": {
                "__codec__": "eventz.marshall.DatetimeCodec",
                "params": {"timestamp": dt_iso1},
            },
            "parent_id": parent_id1,
            "children": {
                "__fcn__": "tests.example.children.Children",
                "name": "Group One",
                "items": [
                    {"__fcn__": "tests.example.child.Child", "name": "Child One",},
                    {"__fcn__": "tests.example.child.Child", "name": "Child Two",},
                    {"__fcn__": "tests.example.child.Child", "name": "Child Three",},
                ],
            },
        },
        {
            "__fcn__": "tests.example.parent.ChildChosen",
            "__version__": 1,
            "msgid": msgid2,
            "timestamp": {
                "__codec__": "eventz.marshall.DatetimeCodec",
                "params": {"timestamp": dt_iso2},
            },
            "parent_id": parent_id1,
            "child": {"__fcn__": "tests.example.child.Child", "name": "Child Three",},
        },
    ]
