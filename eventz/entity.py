from typing import Optional, Dict, Any, Generic, TypeVar
from uuid import uuid4

from eventz.immutable import Immutable

T = TypeVar("T")


class Entity(Generic[T], metaclass=Immutable):
    transform_underscores: bool = False

    @staticmethod
    def make_id() -> str:
        return str(uuid4())

    def __init__(self, uuid: Optional[str] = None):
        self.uuid: str = uuid if uuid is not None else self.make_id()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        if not isinstance(other, Entity):
            return True
        return self.__dict__ != other.__dict__

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = {k: getattr(self, k) for k in vars(self)}
        attrs_string = " ".join([f"{k}={v}" for k, v in attrs.items()])
        return f"{class_name}({attrs_string})"

    def _mutate(self, name, value) -> T:
        return Immutable.__mutate__(
            self, name, value, self.transform_underscores
        )

    def _mutate_all(self, updates: Dict[str, Any]) -> T:
        entity = self
        for name, value in updates.items():
            entity = Immutable.__mutate__(
                entity, name, value, self.transform_underscores
            )
        return entity
