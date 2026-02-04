import typing
import inspect


T = typing.TypeVar("T")


_registry: dict[type, type] = dict()


def register(interface: type[T], implementation: type[T]) -> None:
    if not inspect.isclass(implementation):
        raise TypeError("Class reference expected and not and instance")
    if not inspect.isclass(interface):
        raise TypeError("Class reference expected and not and instance")
    if not issubclass(implementation, interface) or implementation is interface:
        raise TypeError("Implementation is not a subclass of interface")
    _registry[interface] = implementation


def get(interface: type[T]) -> T:
    if interface not in _registry:
        raise LookupError(f"No `{interface.__name__}` implementation found")
    clazz = _registry[interface]
    return typing.cast(T, clazz())
