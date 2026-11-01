# Proposal

## Why

abookie is a new audiobook player with no code, toolchain, or architecture yet. Before any feature work starts, the project needs one agreed stack, one layering model, and one testing discipline. Without them, the first features would each make those decisions separately and inconsistently. Settling them now, while the repository is empty, costs least.

## What Changes

- Choose the toolchain: Python >= 3.12 managed with uv; ruff for lint and format; pyright for type checking; pytest with pytest-qt and pytest-cov for tests.
- Choose the runtime dependencies: PySide6 (Qt 6) for the UI, libmpv through python-mpv for playback, mutagen for tags, sqlite3 (stdlib) for persistence, platformdirs for per-OS paths.
- Establish the architecture: a pure-Python **core** that defines ports, **platform** adapters that implement those ports (mpv, mutagen, SQLite, filesystem, OS integration), and a thin **ui** layer.
- Enforce the layering automatically (import-linter in the test run) so core never depends on UI or engine libraries.
- Make Test-Driven Development (Red-Green-Refactor) mandatory, with a fake for every port, an injected clock, tiny committed audio fixtures, and a coverage floor of 80%.
- Set the dependency policy: the project's own code is under The Unlicense, GPL/LGPL dependencies are acceptable, third-party code is never vendored or redistributed, and libmpv is a documented system dependency.
- Scope: Linux is the MVP platform. macOS and Windows stay possible because OS-specific code lives only in `platform/`.

## Capabilities

### New Capabilities
- `core`: Cross-cutting requirements for all core capabilities: no dependency on UI, engine, or OS libraries; all external effects go through ports; time comes from an injected clock.
- `ui`: Cross-cutting requirements for all UI capabilities: views hold no business logic and talk to core only through view-models.
- `platform`: Cross-cutting requirements for all platform capabilities: adapters implement core ports, OS-specific code lives only here, and missing system dependencies are reported clearly.

### Modified Capabilities
<!-- none: no specs exist yet -->

## Impact

- New `pyproject.toml`, `uv.lock`, and `src/abookie/` package with `core/`, `ui/`, and `platform/` subpackages; new `tests/` tree.
- New system dependency for users and developers: libmpv (distro package `mpv` / `mpv-libs` / `libmpv2`).
- `.githooks/pre-push` gains a test-and-coverage check alongside the existing gir check.
- `AGENTS.md` gains the real build, lint, type-check, and test commands once the toolchain exists.
- Gives all future changes (starting with `library-model`) their layering and testing rules.
