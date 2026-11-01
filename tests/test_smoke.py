"""Smoke tests for the project skeleton."""

import importlib


def test_package_imports_and_has_version() -> None:
    abookie = importlib.import_module("abookie")
    assert isinstance(abookie.__version__, str)
    assert abookie.__version__


def test_runtime_dependencies_importable() -> None:
    for name in ("PySide6", "mutagen", "platformdirs"):
        importlib.import_module(name)


def test_layer_packages_exist() -> None:
    for name in ("abookie.core", "abookie.ui", "abookie.platform", "abookie.app"):
        importlib.import_module(name)
