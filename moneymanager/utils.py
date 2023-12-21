import functools
import inspect
from collections.abc import Callable
from types import GenericAlias
from importlib import import_module
from threading import Lock
from typing import ParamSpec, TypeVar

_Bindings = dict[type, object]
_T = TypeVar("_T")
_P = ParamSpec("_P")


class InjectionContainer:
    def __init__(self) -> None:
        self._lock = Lock()
        self._bindings: _Bindings = {}
        self._overridden_bindings: _Bindings = {}

    def __getitem__(self, key: type[_T]) -> _T:
        if not inspect.isclass(key):
            raise TypeError(f"{key} is not a valid type")
        with self._lock:
            if key not in self._bindings:
                raise KeyError(f"No binding found for type {key}")
            return self._overridden_bindings.get(key) or self._bindings[key]

    def __setitem__(self, key: type[_T], value: _T) -> None:
        self._validate_binding(key, value)
        with self._lock:
            self._bindings[key] = value

    def override(self, key: type[_T], value: _T) -> None:
        """Create temporary binding."""
        self._validate_binding(key, value)
        with self._lock:
            self._overridden_bindings[key] = value

    def reset_override(self):
        """Reset all temporary bindings."""
        with self._lock:
            self._overridden_bindings.clear()

    def inject(self, *params: str) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
        """Return decorator that injects provided parameters."""

        def decorator(func: Callable[_P, _T]) -> Callable[_P, _T]:
            annotations = inspect.get_annotations(func)
            for param_name in params:
                if param_name not in annotations:
                    raise TypeError(f"No annotation found for parameter {param_name}")

            @functools.wraps(func)
            def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                for param_name in params:
                    call_args = inspect.signature(func).bind_partial(*args, **kwargs)
                    if param_name not in call_args.arguments:
                        key = self._extract_type(annotations[param_name])
                        call_args.arguments[param_name] = self.__getitem__(key)
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
        if key is type:
            raise TypeError(f"Binding for {type} is ambiguous")
        if not (inspect.isclass(key) and isinstance(value, key)):
            raise TypeError(
                f"Can't assign instance of type {type(value)} to type {key}"
            )

    def _extract_type(self, key: type | GenericAlias) -> type:
        if not isinstance(key, GenericAlias):
            return key
        if key.__origin__ is not type:
            raise TypeError(f"Generic alias of {key.__origin__} is not supported")
        return self._parse_generic_type_alias(key)

    def _parse_generic_type_alias(self, type_alias: GenericAlias) -> type:
        if len(type_alias.__args__) != 1:
            raise TypeError("Generic type alias with several arguments is ambiguous")
        return type(type_alias.__args__[0])
