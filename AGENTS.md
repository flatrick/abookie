# AGENTS.md

This file guides AI coding agents (Claude Code and others) working in this repository.

## Project state

abookie is an audiobook player. Linux is the MVP target. macOS and Windows must stay possible, but no effort goes into them before the Linux MVP. The project's own code is released under The Unlicense.

The toolchain, layering and test suite exist; there are no user-facing features yet. Read the specs and planned changes before implementing anything:

- `openspec/specs/{core,platform,ui}/spec.md`: the cross-cutting rules for each layer (from the archived `project-foundation` change).
- `openspec/changes/archive/2026-11-01-project-foundation/design.md`: why the stack, layering and testing approach were chosen.
- `openspec/changes/library-model/`: planned next. Library roots, structures, scanning, book identity, listening state.

Once a change is archived, `openspec/specs/` is the source of truth for its requirements. Do not invent build/test commands; use the ones under [Commands](#commands).

## Architecture

The code is split into three layers. Tests enforce the boundaries between them:

- `core`: pure application logic. Defines ports (interfaces) for every external effect. Never imports UI, playback engine, tag, storage, or OS libraries, and gets time only from an injected clock.
- `platform`: adapters implementing core ports (playback engine, tags, storage, filesystem, OS integration). The only place OS-specific code may live.
- `ui`: views and view-models. Views hold no business logic and never call platform adapters directly.

Rationale and details are in `openspec/changes/archive/2026-11-01-project-foundation/design.md`.

## Commands

Python >= 3.12, managed with [uv](https://docs.astral.sh/uv/). libmpv is a system dependency (see `README.md`).

| Command | What it does |
|---------|--------------|
| `./dev-setup.sh` | Apply the expected local git settings (hooks, fast-forward-only merge and pull, rebase options). Run once per clone. |
| `uv sync` | Create/update `.venv` from `uv.lock`, including the `dev` tools. |
| `uv run pytest` | Run all tests (markers `unit`, `integration`, `ui`, `tooling`) with coverage; fails below 80%. |
| `uv run pytest -m unit` | Run one marker only (`--no-cov` skips the coverage floor for partial runs). |
| `uv run ruff check --fix .` | Lint and apply safe fixes. |
| `uv run ruff format .` | Format the code. |
| `uv run pyright` | Type-check (strict for all of `src`, basic for `tests`). |
| `uv run lint-imports` | Check the layer contracts (also run by `tests/architecture/test_layers.py`). |
| `uv run abookie` | Start the application. |
| `tests/fixtures/make_fixtures.sh` | Regenerate the committed audio fixtures (needs ffmpeg). |

Git hooks (enabled per clone with `./dev-setup.sh` or `gir init`; each skips with a warning when its tool is missing):

- `pre-commit`: runs `ruff check --fix` and `ruff format` on staged `*.py` files. If anything changed, the commit is aborted and the files to re-stage are listed.
- `commit-msg`: gir checks the message against Conventional Commits.
- `pre-push`: `.githooks/check-all.sh` runs `ruff check`, `ruff format --check`, `pyright` and `pytest` (with coverage), then gir checks the pushed commits. Any failure blocks the push. Run `.githooks/check-all.sh` directly to get the same checks before pushing.

## Development rules

- **TDD is mandatory.** Use Red-Green-Refactor for every change: write a failing test first, then the minimal code that passes it, then refactor with tests green. Do not write implementation code without a failing test that requires it.
- **Never vendor or redistribute third-party code.** Declare dependencies in `pyproject.toml`. Native libraries (libmpv) are documented system dependencies. GPL/LGPL dependencies are acceptable.

## Writing (ASD-STE100)

All text in this repository MUST follow [ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/). This applies to documentation, OpenSpec artifacts, code comments, docstrings, commit messages, and text that the user sees in the application.

The main rules are:

- Use only approved words, and use each word with its approved meaning only. You can also use technical names and technical verbs (for example, `scan`, `rescan`, `merge`, `libmpv`).
- Write short sentences: 20 words or fewer for procedures, 25 words or fewer for descriptions.
- Write one instruction in each sentence. Use the imperative form for instructions.
- Use the active voice.
- Use the same term for the same thing every time. Do not use synonyms.
- Write paragraphs of 6 sentences or fewer.

The project dictionary is in [`STE-DICTIONARY.md`](STE-DICTIONARY.md). It gives the technical names and technical verbs of this project, with their meanings. When the dictionary gives a word, you MUST use that word with that meaning. When we decide on a new word, add it to the dictionary first.

## Spec-driven workflow (OpenSpec)

Changes are planned with [OpenSpec](https://github.com/Fission-AI/OpenSpec) using the `spec-driven` schema (`openspec/config.yaml`).

- `openspec/changes/<name>/` holds in-progress changes: `proposal.md`, `design.md`, `tasks.md`, and delta specs under `specs/<capability-path>/spec.md`.
- `openspec/changes/archive/` holds completed changes.
- `openspec/specs/` holds the canonical specs. Only `openspec archive` writes these, so never edit them by hand.
- Specs are nested under three top-level areas that mirror the code layers: `core/`, `ui/`, `platform/` (e.g. `specs/core/library/identity/spec.md`). An area's own `spec.md` (e.g. `specs/core/spec.md`) holds only cross-cutting requirements that apply to everything beneath it.
- The project commands live in `.claude/commands/opsx/`: `/opsx:propose`, `/opsx:new`, `/opsx:continue`, `/opsx:apply`, `/opsx:verify`, `/opsx:archive`, `/opsx:explore`, `/opsx:sync`, `/opsx:update`, `/opsx:onboard`.
- Propose/new/continue are planning only. They never edit project code, and implementation starts only through `/opsx:apply` on a later request.
- **Commit the plan before any code.** A change's artifacts (proposal, design, specs, tasks) must be committed before its first code change. If `tasks.md` was not part of that commit, it gets a commit of its own. Never run `/opsx:apply` on a change unless git history has at least one commit containing its full set of artifacts, including `tasks.md`, and the change folder has no uncommitted edits.
- **Archiving is a single commit.** `openspec archive "<name>"` (without `--yes`) moves the change to `openspec/changes/archive/` and writes the canonical specs. Commit that move, the spec updates and any follow-up edits the archive requires (such as `AGENTS.md` pointers) together in one commit.
- **Apply in a worktree on its own branch.** `/opsx:apply` work never happens in the main clone. Each change gets a git worktree under `.worktrees/` (gitignored) on a branch named `change/<change-name>`, so several changes can be in progress on one machine:
  ```sh
  git worktree add .worktrees/<change-name> -b change/<change-name>   # from the commit holding the plan
  cd .worktrees/<change-name> && uv sync                              # each worktree has its own .venv
  ```
  All edits, test runs and commits for the change happen inside that worktree. If it already exists, continue there. The git hooks work in every worktree, because `core.hooksPath` is shared repository config.
- Validate with `openspec validate --all`, or `openspec validate --type change <name>` for a single change.
- Project-wide constraints and per-artifact rules (including the TDD rule for `tasks.md` and the spec layout) live in the `context:` / `rules:` sections of `openspec/config.yaml`. Follow them when writing artifacts.

## Commits (gir / git-it-right)

Commit messages are checked by [gir](https://github.com/flatrick/git-it-right) against Conventional Commits: `<type>[(scope)][!]: <description>`.

- **Stage hunks, not files.** Stage only the hunks that belong to the commit. Do not use `git add <file>`, `git add .`, `git add -A` or `git commit -a`.
  - Use `git add -p` to select the hunks.
  - If you cannot use an interactive command, write the selected hunks to a patch file. Then stage it with `git apply --cached <patch>`.
  - For a new file, first run `git add -N <file>`. Then stage its hunks.
  - Before you commit, examine the staged hunks with `git diff --cached`.
- Allowed types (from `.girconfig`): `feat fix docs style refactor perf test build ci chore revert`. The aliases `feature` and `bugfix` map to `feat` and `fix`. The subject can be at most 72 characters.
- Hooks live in `.githooks/` (commit-msg, pre-push). Running `./dev-setup.sh` or `gir init` once per clone sets `core.hooksPath` to point at them. If gir is not installed, the hooks skip the check instead of failing.
- To check a range of commits: `gir lint --range main..HEAD`. When a commit is rejected, `gir explain <rule>` explains the rule it broke.
- Optional changelog/version: `git-cliff -o CHANGELOG.md` and `git-cliff --bumped-version` (configured in `cliff.toml`).

## Branches and merging

History on `main` is linear: merges are fast-forward only, so rebasing is routine.

1. **Review the branch before merging.** Read every commit on it (`git log --reverse main..change/<change-name>`). If the commits do not tell a clean story, rebuild them: `git reset --soft $(git merge-base main HEAD)` and recommit the work as proper Conventional Commits (see above). Otherwise tidy them with `git rebase -i main`.
2. **Rebase onto the current `main`:** `git rebase main`, then rerun the checks (`.githooks/check-all.sh`).
3. **Fast-forward merge only:** from the main clone, `git merge --ff-only change/<change-name>`, then `git push`. Never create merge commits or squash merges.
4. **Clean up:** `git worktree remove .worktrees/<change-name>` and `git branch -d change/<change-name>`.

Run `./dev-setup.sh` once per clone. It sets `merge.ff only` and `pull.ff only`, so a plain `git merge` or `git pull` can only fast-forward.

GitHub enforces the same rules. The `main` ruleset requires linear history and blocks force pushes and deletion. Merge commits and squash merging are disabled. GitHub has no fast-forward button: its "Rebase and merge" recreates the commits with new SHAs. Merge locally with `--ff-only` and push instead.

## Formatting

`.editorconfig` and `.gitattributes` enforce UTF-8 and LF line endings (CRLF only for `*.cmd`, `*.bat` and `*.sln`). Indentation is 4 spaces by default, 2 for YAML/JSON/TOML, and tabs for Makefiles.
