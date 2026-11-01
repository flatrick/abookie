#!/usr/bin/env bash
# Regenerate the tiny audio fixtures used by the test suite.
#
# Requires ffmpeg (with libmp3lame, libopus and the native AAC encoder).
# Running the tests does NOT require ffmpeg: the outputs are committed.
#
# Outputs (each a few seconds of mono silence, well under 50 KB):
#   silence.mp3   3 s, MP3
#   silence.opus  3 s, Opus in Ogg
#   chapters.m4b  4 s, AAC in MP4 with 2 chapters ("Chapter 1" at 0 s,
#                 "Chapter 2" at 2 s), written as both QuickTime and Nero
#                 (chpl) chapters so mpv and mutagen can read them.
#
# Usage: tests/fixtures/make_fixtures.sh
set -euo pipefail

cd "$(dirname "$0")"

common=(-hide_banner -loglevel error -y -f lavfi)
silence() { echo "anullsrc=r=$1:cl=mono:d=$2"; }

ffmpeg "${common[@]}" -i "$(silence 22050 3)" \
    -map_metadata -1 -c:a libmp3lame -b:a 32k silence.mp3

ffmpeg "${common[@]}" -i "$(silence 48000 3)" \
    -map_metadata -1 -c:a libopus -b:a 16k silence.opus

metadata=$(mktemp)
trap 'rm -f "$metadata"' EXIT
cat > "$metadata" <<'META'
;FFMETADATA1
title=Chapters Fixture

[CHAPTER]
TIMEBASE=1/1000
START=0
END=2000
title=Chapter 1

[CHAPTER]
TIMEBASE=1/1000
START=2000
END=4000
title=Chapter 2
META

ffmpeg "${common[@]}" -i "$(silence 22050 4)" -i "$metadata" \
    -map 0:a -map_metadata 1 -map_chapters 1 \
    -c:a aac -b:a 24k -f ipod chapters.m4b

ls -l silence.mp3 silence.opus chapters.m4b
