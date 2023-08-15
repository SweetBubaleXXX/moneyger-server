import functools
import inspect
from collections.abc import Callable
from threading import Lock
from typing import ParamSpec, TypeVar

Bindings = dict[type, object]
T = TypeVar("T")
P = ParamSpec("P")


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
        self._validate_binding(key, value)
        with self._lock:
            self._bindings[key] = value

    def override(self, key: type[T], value: T) -> None:
        self._validate_binding(key, value)
        with self._lock:
            self._overridden_bindings[key] = value

    def reset_override(self):
        with self._lock:
            self._overridden_bindings.clear()

    def inject(self, *params: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @functools.wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> T:
                for param_name in params:
                    if param_name not in kwargs:
                        kwargs[param_name] = self.__getitem__(annotations[param_name])
                return func(*args, **kwargs)

            annotations = inspect.get_annotations(func)
            for param_name in params:
                if param_name not in annotations:
                    raise ValueError(f"No annotation found for parameter {param_name}")
            return inner

        return decorator

    def _validate_binding(self, key, value):
        if not (inspect.isclass(key) and isinstance(value, key)):
            raise TypeError(
                f"Can't assign instance of type {type(value)} to type {key}"
            )
