import inspect
import functools
from collections.abc import Callable
from threading import Lock
from typing import TypeVar

Bindings = dict[type, object]
T = TypeVar("T")


class InjectionContainer:
    def __init__(self) -> None:
        self._lock = Lock()
        self._bindings: Bindings = {}
        self._overridden_bindings: Bindings = {}

    def __getitem__(self, key: type[T]) -> T:
        if not inspect.isclass(key):
            raise TypeError
        with self._lock:
            if key not in self._bindings:
                raise KeyError(f"No binding found for type {key}")
            return self._overridden_bindings.get(key) or self._bindings[key]

    def __setitem__(self, key: type[T], value: T) -> None:
        if not (inspect.isclass(key) and isinstance(value, key)):
            raise TypeError(
                f"Can't assign instance of type {type(value)} to type {key}"
            )
        with self._lock:
            self._bindings[key] = value

    def inject(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def inner(*args, **kwargs):
            pass

        return inner

    def override(self, key: type[T], value: T) -> None:
        pass

    def reset_override(self):
        with self._lock:
            self._overridden_bindings.clear()
