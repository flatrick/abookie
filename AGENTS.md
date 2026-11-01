# AGENTS.md

This file guides AI coding agents (Claude Code and others) working in this repository.

## Project state

abookie is an audiobook player. Linux is the MVP target. macOS and Windows must stay possible, but no effort goes into them before the Linux MVP. The project's own code is released under The Unlicense.

There is no application code, build system, or test suite yet. The stack and architecture are **decided and planned** in OpenSpec changes. Read them before implementing anything:

- `openspec/changes/project-foundation/`: toolchain, dependencies, layering, testing approach.
- `openspec/changes/library-model/`: library roots, structures, scanning, book identity, listening state.

Once a change is archived, `openspec/specs/` is the source of truth for its requirements. Do not invent build/test commands. Applying `project-foundation` adds them here.

## Architecture

The code is split into three layers. Tests enforce the boundaries between them:

- `core`: pure application logic. Defines ports (interfaces) for every external effect. Never imports UI, playback engine, tag, storage, or OS libraries, and gets time only from an injected clock.
- `platform`: adapters implementing core ports (playback engine, tags, storage, filesystem, OS integration). The only place OS-specific code may live.
- `ui`: views and view-models. Views hold no business logic and never call platform adapters directly.

Rationale and details are in `openspec/changes/project-foundation/design.md`.

## Development rules

- **TDD is mandatory.** Use Red-Green-Refactor for every change: write a failing test first, then the minimal code that passes it, then refactor with tests green. Do not write implementation code without a failing test that requires it.
- **Never vendor or redistribute third-party code.** Declare dependencies in `pyproject.toml`. Native libraries (libmpv) are documented system dependencies. GPL/LGPL dependencies are acceptable.

## Spec-driven workflow (OpenSpec)

Changes are planned with [OpenSpec](https://github.com/Fission-AI/OpenSpec) using the `spec-driven` schema (`openspec/config.yaml`).

- `openspec/changes/<name>/` holds in-progress changes: `proposal.md`, `design.md`, `tasks.md`, and delta specs under `specs/<capability-path>/spec.md`.
- `openspec/changes/archive/` holds completed changes.
- `openspec/specs/` holds the canonical specs. Only `openspec archive` writes these, so never edit them by hand.
- Specs are nested under three top-level areas that mirror the code layers: `core/`, `ui/`, `platform/` (e.g. `specs/core/library/identity/spec.md`). An area's own `spec.md` (e.g. `specs/core/spec.md`) holds only cross-cutting requirements that apply to everything beneath it.
- The project commands live in `.claude/commands/opsx/`: `/opsx:propose`, `/opsx:new`, `/opsx:continue`, `/opsx:apply`, `/opsx:verify`, `/opsx:archive`, `/opsx:explore`, `/opsx:sync`, `/opsx:update`, `/opsx:onboard`.
- Propose/new/continue are planning only. They never edit project code, and implementation starts only through `/opsx:apply` on a later request.
- **Commit the plan before any code.** A change's artifacts (proposal, design, specs, tasks) must be committed before its first code change. If `tasks.md` was not part of that commit, it gets a commit of its own. Never run `/opsx:apply` on a change unless git history has at least one commit containing its full set of artifacts, including `tasks.md`, and the change folder has no uncommitted edits.
- Validate with `openspec validate --all`, or `openspec validate --type change <name>` for a single change.
- Project-wide constraints and per-artifact rules (including the TDD rule for `tasks.md` and the spec layout) live in the `context:` / `rules:` sections of `openspec/config.yaml`. Follow them when writing artifacts.

## Commits (gir / git-it-right)

Commit messages are checked by [gir](https://github.com/flatrick/git-it-right) against Conventional Commits: `<type>[(scope)][!]: <description>`.

- Allowed types (from `.girconfig`): `feat fix docs style refactor perf test build ci chore revert`. The aliases `feature` and `bugfix` map to `feat` and `fix`. The subject can be at most 72 characters.
- Hooks live in `.githooks/` (commit-msg, pre-push). Running `gir init` once per clone sets `core.hooksPath` to point at them. If gir is not installed, the hooks skip the check instead of failing.
- To check a range of commits: `gir lint --range main..HEAD`. When a commit is rejected, `gir explain <rule>` explains the rule it broke.
- Optional changelog/version: `git-cliff -o CHANGELOG.md` and `git-cliff --bumped-version` (configured in `cliff.toml`).

## Formatting

`.editorconfig` and `.gitattributes` enforce UTF-8 and LF line endings (CRLF only for `*.cmd`, `*.bat` and `*.sln`). Indentation is 4 spaces by default, 2 for YAML/JSON/TOML, and tabs for Makefiles.
