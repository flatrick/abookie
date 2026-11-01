"""Fixtures for platform tests that need real system dependencies."""

import importlib
from types import ModuleType

import pytest


@pytest.fixture
def libmpv() -> ModuleType:
    """The python-mpv module, or skip the test when libmpv is not installed."""
    try:
        return importlib.import_module("mpv")
    except OSError as error:
        pytest.skip(f"libmpv is not installed ({error}); see README.md")
