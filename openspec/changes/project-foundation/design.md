# Design

## Context

The repository has scaffolding only: git hooks (gir), OpenSpec, editor and line-ending config, and the Unlicense. No code, toolchain, or package layout exists. See proposal.md for the reasons. The project-wide constraints (Linux-first MVP, Unlicense, no redistribution) live in `openspec/config.yaml`. The behavioral rules this design must satisfy are in `specs/core`, `specs/ui` and `specs/platform`.

## Goals / Non-Goals

**Goals:**
- One toolchain that a contributor on any Linux distro can set up with `uv sync` plus a single distro package (libmpv).
- A layering that makes nearly all behavior unit-testable without Qt, mpv, or a filesystem.
- Automated enforcement of the layering and the coverage floor, not just a convention.
- A dependency set that already runs on macOS and Windows, so a later port is packaging work, not a rewrite.

**Non-Goals:**
- Packaging for distribution (Flatpak, AppImage, PyPI release, installers). Not bundling dependencies is a deliberate policy for now.
- macOS/Windows adapters (SMTC, NowPlaying), CI configuration, and any user-facing feature.

## Decisions

### Layering: core / ports / platform / ui

```
  +-------------------------------------------+
  | ui         PySide6 views + view-models    |
  +---------------------+---------------------+
                        | uses
  +---------------------v---------------------+
  | core       pure logic; defines ports      |
  +-----+-------------+-------------+---------+
        ^ implements  ^             ^
  +-----+------+ +----+-------+ +---+-----------------+
  | platform/  | | platform/  | | platform/linux/     |
  | mpv engine | | sqlite,    | | MPRIS, ...          |
  |            | | mutagen,fs | | (macos/, windows/   |
  +------------+ +------------+ |  later)             |
                                +---------------------+
  app wiring (composition root) builds adapters and injects them into core
```

- Package layout: `src/abookie/{core,ui,platform,app}`. `app` is the composition root and the only module that imports all layers.
- Ports are `typing.Protocol` classes in core. Test doubles live in `tests/fakes/`, one per port.
- **import-linter** contracts, run inside pytest, enforce the layer rules: core imports nothing from ui/platform or third-party UI/engine/tag/storage libs; ui does not import platform.
- *Alternative considered*: a flat package with conventions only. Rejected because conventions drift, and the TDD goal depends on core staying pure.

### UI: PySide6 (Qt 6)
- pip wheels on Linux, macOS and Windows; looks acceptable on any desktop (the primary developer uses i3, not GNOME); LGPL.
- *Alternative*: GTK4 + libadwaita via PyGObject. Most native on GNOME, but it needs system packages to install and is hard to ship on Windows/macOS.

### Playback engine: libmpv via python-mpv
- FFmpeg-backed format coverage (m4b, m4a, mp3, opus, ogg, flac); native chapter list for m4b; pitch-preserving speed (`scaletempo2`); playlists for multi-file books; runs on all three OSes.
- libmpv is a **system dependency**, detected at startup (see `specs/platform`).
- *Alternatives*: GStreamer (Linux-native, but needs a PyGObject stack and is hard to package elsewhere); QtMultimedia (no chapter API, and pitch compensation depends on the Qt version).

### Supporting libraries
- **mutagen**: tags, chapters and embedded covers, read without starting playback (needed for library scanning).
- **sqlite3** (stdlib): the tag cache and listening state; handles frequent small writes safely.
- **platformdirs**: per-OS config, data and cache directories.

### Tooling
- **uv**: environment, lockfile (`uv.lock`), Python version pin. Build backend: `uv_build` (or hatchling if it falls short).
- **ruff**: lint and format, configured in `pyproject.toml`, following `.editorconfig` (4 spaces).
- **pyright**: type checking in strict mode for `core`, basic mode elsewhere.
- **Python >= 3.12**: covers current distros. The developer runs 3.14.

### Testing approach (TDD is mandatory)

```
  slow/few   ui           pytest-qt on view-models & signals (offscreen QPA)
             platform     integration tests: real libmpv/mutagen/sqlite on fixtures
  fast/many  core         unit tests with fakes; no I/O; injected FakeClock
```

- Red-Green-Refactor for every task (see `rules.tasks` in config.yaml).
- Pytest markers `unit`, `integration`, `ui`. The default run includes all of them. Integration tests skip with a clear reason if libmpv is absent.
- **Audio fixtures**: tiny committed files (a few seconds of silence: mp3, opus, m4b with chapters), produced by a documented script in `tests/fixtures/`. Regenerating them needs ffmpeg; running the tests does not.
- **Coverage**: pytest-cov with `fail_under = 80`.
- **Hooks**: `.githooks/pre-push` runs ruff, pyright and pytest (with coverage) in addition to gir. The checks are skipped with a warning if uv is not installed, matching how the gir hook behaves.

### Dependency and licensing policy
- Own code: The Unlicense. GPL/LGPL dependencies are accepted.
- Dependencies are declared only in `pyproject.toml`. Nothing is vendored. A third-party notices file becomes necessary only if bundled distribution (Flatpak or installers) is adopted later.
- A short `CONTRIBUTING.md` asks contributors to dedicate their contributions to the public domain (the unlicense.org waiver).

## Risks / Trade-offs

- [libmpv missing or an incompatible version on a user system] → Detect it at startup with an actionable message. Document the distro package names in the README.
- [python-mpv is a ctypes binding, so API mismatches surface at runtime] → Integration tests against the real libmpv. Keep all python-mpv usage inside one adapter.
- [Qt event loop vs mpv event thread] → The mpv adapter marshals events onto the Qt thread through signals. Core never sees threads.
- [80% coverage pushes toward testing trivial code] → Exclude the composition root and generated code from coverage.
- [Strict pyright on core slows early work] → Accepted. Core is where correctness matters most.

## Open Questions

- Build backend: `uv_build` vs hatchling. Either works; decide during implementation.
- Exact pyright strictness for ui/platform, tuned once real code exists.
