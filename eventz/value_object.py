from typing import Generic, TypeVar

from eventz.immutable import Immutable

T = TypeVar("T")


class ValueObject(Generic[T], metaclass=Immutable):
    transform_underscores: bool = False

    def __eq__(self, other) -> bool:
        if not isinstance(other, ValueObject):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        if not isinstance(other, ValueObject):
            return True
        return self.__dict__ != other.__dict__

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = {k: getattr(self, k) for k in vars(self)}
        if "__immutable__" in attrs:
            del attrs["__immutable__"]
        attrs_string = " ".join([f"{k}={v}" for k, v in attrs.items()])
        return f"{class_name}({attrs_string})"

    def _mutate(self, name, value) -> T:
        return Immutable.__mutate__(
            self, name, value, self.transform_underscores
        )

    @classmethod
    def create(cls, **kwargs) -> T:
        """
        Since due to immutable mutations and event replays __init__
        is called with great frequency, the actual creation of the
        object from a domain event PoV should always be done via classmethod
        .create(). This is where we emit any "created" events etc,
        guaranteeing we only ever get one.
        """
        return cls(**kwargs)
