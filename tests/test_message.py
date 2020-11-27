import pytest

from eventz.messages import Event


class NoVersion(Event):
    pass


class Example(Event):
    __version__: int = 1


def test_a_message_must_always_have_a_schema_version_set_on_the_class():
    with pytest.raises(TypeError):
        assert NoVersion()
    example_event_message = Example()
    assert example_event_message.__version__ == 1
