"""The committed audio fixtures exist, stay tiny, and have the expected shape."""

from pathlib import Path

import pytest
from mutagen.mp4 import MP4

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).resolve().parent
MAX_BYTES = 50 * 1024


@pytest.mark.parametrize("name", ["silence.mp3", "silence.opus", "chapters.m4b"])
def test_fixture_exists_and_is_small(name: str) -> None:
    path = FIXTURES / name
    assert path.is_file(), (
        f"missing fixture {name}; run tests/fixtures/make_fixtures.sh"
    )
    assert path.stat().st_size < MAX_BYTES


def test_m4b_has_two_chapters() -> None:
    chapters = MP4(FIXTURES / "chapters.m4b").chapters
    assert chapters is not None
    assert len(chapters) == 2
