# Proposal

## Why

An audiobook player has to remember where the listener is in every book, not only the current one, so that people can switch between books freely. That requires a library model: where books live, what counts as a book, how a book is recognized again after its files are moved or renamed, and how listening state is kept safe. This model comes before playback features, because resuming, the book list and chapters all depend on it.

## What Changes

- **Library roots**: the library is a list of one or more root folders. Roots cannot be nested. The app always has at least one root (asked for on first run).
- **Structures**: each root declares the folder structure of its books, chosen from presets that are stored internally as templates (`{author}/{series}/{title}` plus a leaf type of `file` or `folder`). User-written templates are a later addition with no data model change.
- **Scanning**: books are discovered by scanning a root against its structure, when the root is added and when the user asks for a rescan. There is no live file watching.
- **Warning log**: anything that does not match the root's structure is logged per root with a reason code. The user resolves an entry by changing the structure, moving the files themselves (the app never moves or renames user files), or excluding the path.
- **Book identity**: each book has a set of identity claims stored in an open-ended identity table. The MVP uses absolute path, path relative to its root, and tags, matched in that order. A tag match asks the user to confirm. Content fingerprinting is deferred to a later investigation.
- **Cache vs listening state**: the metadata cache (tags, duration, chapters, cover) can be thrown away and rebuilt. Listening state (position, speed, last played, finished) is never silently lost.
- **Outside-root refusal**: the MVP refuses to handle audio outside every root and tells the user why. How to support such files is a later investigation.
- **UI**: first-run root setup, root management with structure selection, the warning log view, and a book list sorted by last played that shows progress.

## Capabilities

### New Capabilities
- `core/library`: Library roots: at least one, no nesting, unreachable roots, refusal of paths outside every root.
- `core/library/structures`: Structure presets stored as templates, leaf types, disc subfolders, deriving books from paths.
- `core/library/scanning`: Scan triggers, the warning log with reason codes, per-root exclusions.
- `core/library/identity`: The identity claim table, MVP claim kinds, matching order, re-linking moved books, confirmation on tag matches.
- `core/library/state`: The disposable metadata cache vs durable listening state.
- `ui/library`: First-run root setup, root management, warning log view, book list.

### Modified Capabilities
<!-- none: no specs exist yet; depends on project-foundation's core/ui/platform cross-cutting specs -->

## Impact

- Depends on `project-foundation` (layering, ports, TDD rules).
- New core modules for library, structures, scanning, identity and state; new ports for filesystem access, tag reading and persistence; platform adapters for the filesystem, mutagen and SQLite.
- New SQLite schema: roots, structures, exclusions, books, book identities, metadata cache, listening state, warnings.
- New UI: setup wizard, library settings, warning log, book list.
- Investigations recorded for later: content fingerprinting, audio outside roots, user-written templates, live file watching.
