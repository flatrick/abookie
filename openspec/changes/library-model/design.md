# Design

## Context

This change builds on `project-foundation`: core/ports/platform/ui layering, TDD, SQLite, mutagen and PySide6. The requirements are in `specs/core/library/**` and `specs/ui/library`. No library code or schema exists yet. The playback engine itself belongs to a later playback-MVP change. This change only hands a selected book (with its saved position and speed) to a playback session port.

## Goals / Non-Goals

**Goals:**
- A schema that already holds future features (fingerprints, custom templates, more claim kinds) without migrations that touch listening state.
- Scanning and matching as pure core logic, testable against fake directory trees.
- Listening state that survives cache wipes, schema migrations and missing roots.

**Non-Goals:**
- Content fingerprinting, handling audio outside roots, user-written templates, live file watching, moving or renaming files. These are recorded as investigations below.
- Playback, chapters UI, speed control and MPRIS, which belong to the playback-MVP change.

## Decisions

### Data model (SQLite)

```
  roots(id, abs_path UNIQUE, template, leaf_type, added_at)
  exclusions(root_id -> roots, rel_path, UNIQUE(root_id, rel_path))
  warnings(root_id -> roots, rel_path, reason, scanned_at)      -- replaced per scan

  books(id, created_at, status)          -- status: available|unavailable|missing
  book_identities(book_id -> books, kind, value, updated_at,
                  INDEX(kind, value))                -- kind is free text, open set

  metadata_cache(book_id -> books, field, value, source)  -- source: tags|path
  book_files(book_id -> books, rel_order, abs_path, size, mtime, duration)
  chapters(book_id -> books, idx, title, start)

  listening_state(book_id -> books PK, position, speed, last_played, finished)
  pending_matches(found_path, candidate_book_id, root_id)  -- tag matches awaiting user
```

- **Two families of tables.** `metadata_cache`, `book_files` and `chapters` can be truncated at any time. `listening_state` and `book_identities` never get bulk-deleted by code, and their rows are removed only when the user explicitly removes a book.
- **`book_identities` is key/value with an open `kind`**, so adding `fingerprint` later means new rows, not new columns. Unknown kinds are kept and ignored, as the spec requires.
- **Templates are stored as text** (`{author}/{series}/{title}`) along with the leaf type. Presets exist only in UI and core code as named templates. No preset id is persisted.
- **Position model**: a single book-global offset in seconds. Mapping it to file and offset is done from `book_files` durations, so a re-ordered or re-encoded book only invalidates the cache, never the state.
- **Migrations**: the schema version lives in `PRAGMA user_version`. Before any migration the database file is copied to `<name>.bak-v<old>`. A failed migration restores nothing in place and leaves the original untouched (see `specs/core/library/state`).

### Scanning as a pure function

```
  FileSystemPort.walk(root) --> [entries]            (platform adapter)
                                    |
        structure + exclusions ---> | match_structure()   (pure core)
                                    v
                         books_found + warnings
                                    |
        known identities ---------> | resolve_identity()  (pure core)
                                    v
               linked | new | pending_tag_match | missing
                                    |
                     LibraryStore.apply(result)     (single transaction)
```

- `match_structure` takes plain path entries (path, is_dir, size, mtime) and returns books and warnings. Tests drive it with in-memory trees, with no disk access.
- Tag reading happens only for books whose cache is stale (size/mtime changed), through `TagReaderPort` (the mutagen adapter).
- Results are applied in **one transaction per root scan**. A crash mid-scan leaves the previous state intact.
- Audio is recognized by extension (`m4b m4a mp3 opus ogg flac wav aac`) during matching. A file that mutagen cannot read becomes `unreadable-audio`.

### Identity resolution order

```
  found book
    |
    +-- abs_path match ---------------------------> same book
    +-- rel_path match AND old abs_path gone -----> same book, update abs_path
    +-- tags match AND old abs_path gone ---------> pending (ask user)
    +-- otherwise --------------------------------> new book
  known books not found in any reachable root ----> status = missing
  known books under unreachable root -------------> status = unavailable
```

- `tags` claims normalize author and title (casefold, collapse whitespace, strip punctuation) to keep near-duplicates from slipping past.
- The "old abs_path gone" check uses `FileSystemPort.exists`, so it stays testable.

### Root reachability and nesting
- A root is unreachable if its path does not exist or is not a readable directory at scan time. Its books become `unavailable` and are left otherwise untouched.
- Nesting is checked on `realpath` of both paths with `Path.is_relative_to` in both directions.

### Paths outside roots
- One core function, `root_for(path) -> Root | None`. Every entry point that accepts a path from the user (drag and drop, a future CLI argument) goes through it and refuses on `None`.

### UI
- View-models: `LibraryViewModel` (book list, sorted by `last_played`), `RootsViewModel` (add, remove, structure, rescan), `WarningsViewModel` and `MatchConfirmationViewModel`. Views bind to these only.
- "Open location" uses `QDesktopServices.openUrl` through a platform port, so it stays testable.

## Risks / Trade-offs

- [Large libraries make a full scan slow, especially on a NAS] → Only stale books get their tags read. The scan runs off the UI thread with progress shown. Live watching is deferred.
- [rel_path collisions, e.g. two roots both containing `Unknown/Untitled`] → A link happens only when the old location is gone. Otherwise a separate book is created.
- [Tag normalization merges different editions] → Tag matches always need confirmation, and duration is shown so the user can tell them apart.
- [Strict templates reject mixed libraries] → The warning log makes this visible. Users can split the collection across roots. Custom and optional templates come in a later change.
- [Extension-based audio detection misses odd files] → They end up as unmatched noise or as `unreadable-audio`, both visible in the log.

## Migration Plan

This is a new database, so no migration is needed. Schema version 1 is created on first run under `platformdirs.user_data_dir("abookie")`.

## Open Questions

- The exact scan-progress UI (inline in the library vs a dialog). Doesn't affect specs.
- The periodic position-save interval (5–15 s). It's a playback-MVP concern, and only "within the interval" is specified here.

## Later investigations (out of scope, recorded for follow-up changes)

- **Content fingerprinting**: an algorithm that tolerates re-tagging, e.g. hashing audio frames while skipping tag atoms.
- **Audio outside roots**: allow it with reduced claims, offer to add a root, or keep refusing.
- **User-written templates**: optional segments and template validation UI.
- **Live file watching**: inotify on Linux, with an abstraction for other OSes.
