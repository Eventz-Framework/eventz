from typing import TypeVar, Any, Dict

T = TypeVar("T")


class Immutable(type):
    def __new__(mcs, name, bases, dictionary):
        instance = type.__new__(mcs, name, bases, dictionary)
        instance.__setattr__ = _setattr
        instance.__delattr__ = _delattr
        instance.__immutable__ = False
        return instance

    def __call__(cls, *args, **kwargs):
        """
        Allow attributes to be set once on instantiation
        """
        if "__immutable__" in kwargs:
            del kwargs["__immutable__"]
        obj = type.__call__(cls, *args, **kwargs)
        # now instance is instantiated set as immutable
        obj.__immutable__ = True
        return obj

    @staticmethod
    def __mutate__(
        obj: T, name: str, value: Any, transform_underscores: bool = False
    ) -> T:
        """
        Mutates a single parameter of an object and returns a new, updated copy
        If `transform_underscores` is set to True then
        private attributes set as `_attr` will be passed to `__init__` as `attr`
        """
        # obtain a dictionary of the objects attributes
        attrs: Dict[str, Any] = {k: getattr(obj, k) for k in vars(obj)}
        # set the mutated attribute to the new value
        attrs[name] = value
        if transform_underscores:
            new_attrs = {}
            # remove underscore from the start of private properties
            for attr_name, attr_val in attrs.items():
                if attr_name.startswith("_") and attr_name != "__immutable__":
                    attr_name = attr_name[1:]
                new_attrs[attr_name] = attr_val
            attrs = new_attrs
        # return a new instance of the object
        return type(obj)(**attrs)


def _setattr(self, attr, value):
    # we'll only block "setting" once __immutable__ is True
    if self.__immutable__:
        raise AttributeError("An attribute cannot be modified on an immutable object.")
    object.__setattr__(self, attr, value)


def _delattr(self, attr):  # pragma: no cover
    raise AttributeError("An attribute cannot be deleted on an immutable object.")
