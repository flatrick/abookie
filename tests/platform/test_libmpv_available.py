"""libmpv works through python-mpv: later playback adapters can rely on it."""

from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.integration

SILENCE_MP3 = Path(__file__).resolve().parents[1] / "fixtures" / "silence.mp3"


def test_plays_fixture_to_the_end(libmpv: ModuleType) -> None:
    player = libmpv.MPV(
        ao="null", ao_null_untimed=True, vo="null", audio_display="no", config=False
    )
    try:
        player.play(str(SILENCE_MP3))
        player.wait_for_playback(timeout=10)
        # python-mpv returns once the file ends; mpv then reports no file.
        assert player.idle_active
    finally:
        player.terminate()
