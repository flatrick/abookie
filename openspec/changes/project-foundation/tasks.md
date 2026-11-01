# Tasks

Every task follows Red-Green-Refactor: write the named failing test(s) first and watch them fail (RED), add the minimal code or config that passes them (GREEN), then refactor with all tests green.

## 1. Project skeleton and dependencies

- [ ] 1.1 RED: `tests/test_smoke.py::test_package_imports_and_has_version` fails (no project). GREEN: add `pyproject.toml` (name `abookie`, `requires-python = ">=3.12"`, `uv_build` backend, src layout) and `src/abookie/__init__.py` with `__version__`. Verify with `uv sync && uv run pytest tests/test_smoke.py`.
- [ ] 1.2 RED: `tests/test_smoke.py::test_runtime_dependencies_importable` (PySide6, mutagen, platformdirs) fails. GREEN: add runtime deps `PySide6`, `python-mpv`, `mutagen`, `platformdirs` and a `dev` dependency group with `pytest`, `pytest-qt`, `pytest-cov`, `ruff`, `pyright`, `import-linter`. Verify with `uv sync` succeeding, `uv.lock` committed, and the test passing.
- [ ] 1.3 RED: `tests/test_smoke.py::test_layer_packages_exist` (imports `abookie.core`, `abookie.ui`, `abookie.platform`, `abookie.app`) fails. GREEN: create the four subpackages, plus `tests/fakes/` as a package. Verify the test passes.
- [ ] 1.4 Add `README.md` (what abookie is, Linux-first, libmpv install per distro: Arch `mpv`, Debian/Ubuntu `libmpv2`, Fedora `mpv-libs`, dev setup with `uv sync` and `gir init`) and `CONTRIBUTING.md` (TDD rule, public-domain dedication of contributions). Verify the README's dev-setup commands run as written in a fresh clone.

## 2. Automatic formatting and linting

- [ ] 2.1 RED: `tests/tooling/test_ruff_config.py` fails. It writes badly formatted Python with unsorted imports into `tmp_path` and asserts that `ruff format --check` and `ruff check` (run with the project config via `--config pyproject.toml`) both report it. GREEN: add `[tool.ruff]` to `pyproject.toml` (`target-version = "py312"`, 4-space indent per `.editorconfig`, rule sets including `E`, `F`, `I`, `UP`, `B`, `SIM`). Verify the test passes and `uv run ruff check . && uv run ruff format --check .` is clean.
- [ ] 2.2 RED: `tests/tooling/test_pre_commit_hook.py` fails. In a temporary git repo it tests that (a) a commit with a misformatted staged `.py` file is aborted, the file is auto-formatted and auto-fixed, and the message lists the files to re-stage; (b) a clean commit passes; (c) without `uv` on `PATH`, the hook warns and exits 0. GREEN: add `scripts/hooks/format-staged.sh` (runs `ruff format` and `ruff check --fix` on staged `*.py` only, aborts if anything changed so partial staging is never silently rewritten) and `.githooks/pre-commit` calling it. Verify the tests pass.
- [ ] 2.3 RED: `tests/tooling/test_typecheck.py::test_pyright_clean` runs `pyright` and asserts exit 0. Confirm it fails by temporarily adding an unannotated function under `src/abookie/core/`, then remove the function. GREEN: add `[tool.pyright]` (strict for `src/abookie/core`, basic elsewhere, `pythonVersion = "3.12"`). Verify the test passes.
- [ ] 2.4 RED: `tests/tooling/test_pre_push_hook.py` fails. With a temporary repo and a bare remote, it tests that a push is blocked when lint, format, type or test checks fail and allowed when they pass. GREEN: add `scripts/hooks/check-all.sh` (`ruff check`, `ruff format --check`, `pyright`, `pytest` with coverage) and call it from `.githooks/pre-push` **before** gir's final `exec` line (keep the gir-managed part intact; skip with a warning when `uv` is missing, same as gir). Verify the tests pass.
- [ ] 2.5 Add a "Commands" section to `AGENTS.md` (`uv sync`, `uv run pytest`, `uv run ruff check --fix .`, `uv run ruff format .`, `uv run pyright`, `uv run lint-imports`, what each git hook runs). Verify every listed command runs as written.

## 3. Test infrastructure

- [ ] 3.1 RED: `tests/test_pytest_config.py::test_markers_registered` asserts that the markers `unit`, `integration`, `ui` and `tooling` are registered (via `pytestconfig.getini("markers")`). GREEN: add `[tool.pytest.ini_options]` with `--strict-markers`, `testpaths`, the markers, and `QT_QPA_PLATFORM=offscreen` for UI tests (set in `tests/conftest.py`). Verify the test passes.
- [ ] 3.2 RED: `tests/test_pytest_config.py::test_coverage_floor_is_80` asserts the coverage config has `fail_under = 80` and omits `src/abookie/app/*`. GREEN: add `[tool.coverage]` settings and `--cov=abookie` to pytest addopts. Verify `uv run pytest` prints the coverage report and enforces the floor.
- [ ] 3.3 RED: `tests/fixtures/test_fixtures.py` asserts that `silence.mp3`, `silence.opus` and `chapters.m4b` exist, are each under 50 KB, and that `chapters.m4b` has exactly 2 chapters (read with mutagen). GREEN: add `tests/fixtures/make_fixtures.sh` (ffmpeg, a few seconds of silence, documented at the top of the script) and commit its outputs. Verify the test passes without ffmpeg installed.

## 4. Core cross-cutting rules (specs/core)

- [ ] 4.1 RED: `tests/architecture/test_layers.py::test_import_contracts_hold` runs import-linter and fails (no contracts). GREEN: add `[tool.importlinter]` contracts with `include_external_packages = true`: core forbids `abookie.ui`, `abookie.platform`, `abookie.app`, `PySide6`, `mpv`, `mutagen`, `sqlite3`, `platformdirs`, `time`; ui forbids `abookie.platform`. Confirm each contract catches a temporary violating import (including that stdlib modules such as `sqlite3` are covered), then remove it. Verify the test passes.
- [ ] 4.2 RED: `tests/core/test_clock.py::test_fake_clock_fires_scheduled_callback_on_advance` and `::test_fake_clock_now_advances` fail. GREEN: add the `Clock` port (`typing.Protocol`: `now()`, `call_later(delay, callback)` returning a cancel handle) in `src/abookie/core/ports/clock.py` and `tests/fakes/fake_clock.py`. Verify the tests pass with no real sleeping.
- [ ] 4.3 RED: `tests/architecture/test_core_purity.py::test_core_does_not_read_system_clock` walks the AST of every core module and fails on calls to `datetime.now`, `datetime.today`, `date.today` or `datetime.utcnow`. GREEN: none needed if the test passes immediately. Confirm it fails with a temporary offending line, then remove it. Verify the test passes.
- [ ] 4.4 RED: `tests/architecture/test_ports_have_fakes.py::test_every_port_has_a_fake` discovers every `Protocol` in `abookie.core.ports` and fails if `tests/fakes` has no class implementing it (checked structurally). GREEN: register `FakeClock`. Verify the test passes and fails when a port without a fake is added temporarily.

## 5. Platform cross-cutting rules (specs/platform)

- [ ] 5.1 RED: `tests/platform/test_system_clock.py` (marker `integration`) tests that `SystemClock.now()` tracks real time and `call_later` fires on the Qt event loop (pytest-qt `qtbot.waitUntil`). GREEN: add `src/abookie/platform/clock.py` implementing the `Clock` port with `QTimer`. Verify the tests pass.
- [ ] 5.2 RED: `tests/platform/test_sysdeps.py::test_reports_missing_libmpv_with_install_hint` (injected loader raising `OSError`) and `::test_passes_when_libmpv_loads` fail. GREEN: add `src/abookie/platform/sysdeps.py`. Its check returns a result naming the missing library and the per-distro install commands from the README. Verify the tests pass.
- [ ] 5.3 RED: `tests/platform/test_libmpv_available.py` (marker `integration`, skipped with a clear reason when libmpv is absent) loads python-mpv with `ao=null` and plays `tests/fixtures/silence.mp3` to the end. GREEN: no production code. The test confirms the system dependency works for later adapter changes. Verify it passes on a machine with libmpv installed.

## 6. UI cross-cutting rules (specs/ui) and application entry

- [ ] 6.1 RED: `tests/ui/test_main_window.py::test_window_title_comes_from_view_model` (marker `ui`, pytest-qt, offscreen) fails. GREEN: add `MainViewModel` (title) and an empty `MainWindow` that only binds to it. Verify the test passes and the import contracts from 4.1 still hold.
- [ ] 6.2 RED: `tests/test_main.py::test_main_exits_cleanly_when_libmpv_missing` (sysdeps check injected as failing; asserts exit code 1, the message on stderr names the library and the install hint, and no traceback is printed) fails. GREEN: add `src/abookie/app/main.py` (composition root: dependency check, then `QApplication`, then `MainWindow`), a `[project.scripts] abookie = "abookie.app.main:run"` entry and `src/abookie/__main__.py`. Show the same message in a Qt dialog when a display is available. Verify the test passes and `uv run abookie` opens an empty window on Linux.

## 7. Integration check

- [ ] 7.1 In a fresh clone, run `gir init`, `uv sync`, `uv run pytest` (all markers, coverage at least 80%), `uv run lint-imports`, `uv run pyright` and `openspec validate --all`. Make one commit with a deliberately misformatted file to confirm the pre-commit hook auto-formats and aborts, then one push to confirm the pre-push checks run. Verify all of these pass or behave as described.

## Workflow follow-up

- Update `AGENTS.md` "Project state" so it no longer points at `openspec/changes/project-foundation/` once the change is archived.
- Archive with `openspec archive "project-foundation"` after review, then verify that `openspec/specs/core/spec.md`, `ui/spec.md` and `platform/spec.md` exist.
