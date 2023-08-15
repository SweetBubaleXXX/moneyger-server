import functools
import inspect
from collections.abc import Callable
from importlib import import_module
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
            raise TypeError(f"{key} isn't a valid type")
        with self._lock:
            if key not in self._bindings:
                raise KeyError(f"No binding found for type {key}")
            return self._overridden_bindings.get(key) or self._bindings[key]

    def __setitem__(self, key: type[T], value: T) -> None:
        self._validate_binding(key, value)
        with self._lock:
            self._bindings[key] = value

    def override(self, key: type[T], value: T) -> None:
        """Create temporary binding."""
        self._validate_binding(key, value)
        with self._lock:
            self._overridden_bindings[key] = value

    def reset_override(self):
        """Reset all temporary bindings."""
        with self._lock:
            self._overridden_bindings.clear()

    def inject(self, *params: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Return decorator that injects provided parameters."""

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            annotations = inspect.get_annotations(func)
            for param_name in params:
                if param_name not in annotations:
                    raise TypeError(f"No annotation found for parameter {param_name}")

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                for param_name in params:
                    call_args = inspect.signature(func).bind_partial(*args, **kwargs)
                    if param_name not in call_args.arguments:
                        call_args.arguments[param_name] = self.__getitem__(
                            annotations[param_name]
                        )
                return func(*call_args.args, **call_args.kwargs)

            return wrapper

        return decorator

    def bind(self, key: type, name: str, *args, **kwargs) -> None:
        """Import class by `name` and create binding `key: Class(*args, **kwargs)`."""
        module_name, class_name = name.rsplit(".", 1)
        module = import_module(module_name)
        factory = getattr(module, class_name)
        if not issubclass(factory, key):
            raise TypeError(f"Imported class isn't a subclass of {key}")
        self.__setitem__(key, factory(*args, **kwargs))

    def _validate_binding(self, key, value):
        if not (inspect.isclass(key) and isinstance(value, key)):
            raise TypeError(
                f"Can't assign instance of type {type(value)} to type {key}"
            )
