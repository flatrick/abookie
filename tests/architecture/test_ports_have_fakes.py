"""Every port in ``abookie.core.ports`` has a structural fake in ``tests.fakes``."""

import importlib
import inspect
import pkgutil
from types import ModuleType

import pytest

import abookie.core.ports
import tests.fakes

pytestmark = pytest.mark.unit


def _modules(package: ModuleType) -> list[ModuleType]:
    return [package] + [
        importlib.import_module(info.name)
        for info in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]


def _defined_classes(package: ModuleType) -> list[type]:
    return [
        obj
        for module in _modules(package)
        for _, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    ]


def _is_protocol(cls: type) -> bool:
    return bool(getattr(cls, "_is_protocol", False))


def _protocol_members(protocol: type) -> set[str]:
    members: set[str] = set()
    for base in protocol.__mro__:
        if base is object or not _is_protocol(base) or base.__name__ == "Protocol":
            continue
        members.update(
            name
            for name in vars(base)
            if not name.startswith("_")  # skips dunders and typing/abc internals
        )
        members.update(
            name
            for name in getattr(base, "__annotations__", {})
            if not name.startswith("_")
        )
    return members


def _implements(cls: type, protocol: type) -> bool:
    return all(hasattr(cls, member) for member in _protocol_members(protocol))


def _ports() -> list[type]:
    return [cls for cls in _defined_classes(abookie.core.ports) if _is_protocol(cls)]


def _missing_fakes(ports: list[type], fakes: list[type]) -> list[str]:
    return [
        f"{port.__module__}.{port.__qualname__}"
        for port in ports
        if not any(_implements(fake, port) for fake in fakes)
    ]


def test_ports_are_discovered() -> None:
    assert "Clock" in {port.__name__ for port in _ports()}


def test_every_port_has_a_fake() -> None:
    fakes = [cls for cls in _defined_classes(tests.fakes) if not _is_protocol(cls)]
    assert _missing_fakes(_ports(), fakes) == []
