from datetime import datetime

import pytest

from eventz.entity import Entity
from tests.example.child import Child
from tests.example.children import Children
from tests.example.parent import ChildChosen, ParentCreated

parent_id1 = Entity.make_id()
msgid1 = "11111111-1111-1111-1111-111111111111"
msgid2 = "22222222-2222-2222-2222-222222222222"
dt_iso1 = "2020-01-02T03:04:05.123456"
dt_iso2 = "2020-01-02T03:04:06.123456"
dt1 = datetime(2020, 1, 2, 3, 4, 5, 123456)
dt2 = datetime(2020, 1, 2, 3, 4, 6, 123456)


@pytest.fixture
def parent_created_event():
    return ParentCreated(
        aggregate_id=parent_id1,
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
        __seq__=None,
    )


@pytest.fixture
def child_chosen_event():
    return ChildChosen(
        aggregate_id=parent_id1,
        child=Child(name="Child Three"),
        __msgid__=msgid2,
        __timestamp__=dt2,
        __seq__=None,
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
            "__seq__": 1,
            "aggregate_id": parent_id1,
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
            "__seq__": 2,
            "aggregate_id": parent_id1,
            "child": {"__fqn__": "tests.Child", "name": "Child Three",},
        },
    ]