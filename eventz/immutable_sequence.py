from typing import TypeVar, Generic, Iterable, Tuple

T = TypeVar('T')


class ImmutableSequence(Generic[T]):
    def __init__(self, items: Iterable[T]):
        self._items: Tuple[T] = tuple(items)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ImmutableSequence):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        if not isinstance(other, ImmutableSequence):
            return True
        return self.__dict__ != other.__dict__

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = {k: getattr(self, k) for k in vars(self)}
        if "__immutable__" in attrs:  # pragma: no cover
            del attrs["__immutable__"]
        attrs_string = " ".join([f"{k}={v}" for k, v in attrs.items()])
        return f"{class_name}({attrs_string})"

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        for item in self._items:
            yield item

    def __getitem__(self, key) -> T:
        return self._items[key]
