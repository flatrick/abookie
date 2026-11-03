# Design

## Context

This change uses the work of `project-foundation`: the core/ports/platform/ui layers, TDD, SQLite, mutagen and PySide6. The requirements are in `specs/core/library/**` and `specs/ui/library`. There is no library code or schema at this time. A later playback-MVP change adds the playback engine. This change only sends the selected book, with its saved position and speed, to a playback session port.

During the exploration, we changed the model for book detection. The first draft used one template with a fixed depth for each root (`{author}/{series}/{title}`). We examined a real collection of approximately 200 books. No single template agreed with more than approximately 60% of it, because one author folder often contains single books and series. The application never moves files, so the user cannot divide the collection into more roots. This collection is only one example, not a design target. But it shows problems that are frequent in collections:

- The depth of books is different from book to book.
- Author tags can contain a narrator, a publisher or a series name.
- The title of the book is in `album`, not in `title`.
- One book can have files of different formats.
- Some files are not readable.

## Goals / Non-Goals

**Goals:**
- A schema that can hold future features (fingerprints, name patterns that the user writes, more claim kinds). Migrations for these features must not change listening state.
- Book detection, pattern scores, scanning and identity comparison as pure core functions. Tests use directory trees in memory and tag fixtures.
- Listening state that stays safe in all of these conditions:
  - The cache is deleted, or the schema is migrated.
  - Roots are unreachable, or books merge.
  - The database is not readable.

**Non-Goals:**
- Content fingerprints, audio outside the roots, and name patterns that the user writes.
- Settings for each folder, symbolic links, file monitoring, and moving or renaming files.
- The section "Later investigations" records these items.
- Playback, the interval for periodic position saves, the chapters UI, speed control and MPRIS. These items are part of the playback-MVP change.

## Decisions

### Data model (SQLite)

```
  roots(id, path UNIQUE, leaf_mode, name_pattern, added_at)  -- path as entered
  exclusions(root_id -> roots, rel_path, UNIQUE(root_id, rel_path))
  warnings(root_id -> roots, rel_path, reason, scanned_at)      -- replaced per scan

  books(id, created_at, status)          -- status: available|unavailable|missing
  book_identities(book_id -> books, kind, value, updated_at,
                  INDEX(kind, value))                -- kind is free text, open set

  metadata_cache(book_id -> books, field, value, source)  -- source: tags|path
  book_files(book_id -> books, rel_order, abs_path, size, mtime, duration)
  chapters(book_id -> books, idx, title, start)

  listening_state(book_id -> books PK, position, speed, last_played, finished)
  state_conflicts(book_id -> books, position, speed, last_played, finished,
                  from_book_id)                       -- alternatives after a merge
  pending_matches(found_book_id -> books, candidate_book_id -> books)  -- tag-only
```

- **Two families of tables.** The application can delete all rows of `metadata_cache`, `book_files` and `chapters` at any time. The code never deletes many rows of `listening_state`, `state_conflicts` or `book_identities` together. It deletes a row of these tables only after one of these user operations: remove a book, accept a merge, or select a state.
- **`book_identities` is a key/value table with an open `kind`.** Thus a later `fingerprint` claim adds new rows, not new columns. The application keeps claims of unknown kinds and does not use them.
- **`roots.name_pattern` is text** (`{author}/…/{title}` or `{author} - {title}`). Thus name patterns that the user writes need no schema change. The application does not keep a preset identifier. `leaf_mode` is `folder` or `file`.
- **`roots.path` is the path as the user wrote it.** The application makes each `abs_path` claim from `root.path / rel_path`. If the user changes the target of a symbolic link that is a root, its books move with it. The nesting check uses the `realpath` of the two paths.
- **Books have no `root_id`.** The application finds the root of a book from its `abs_path` claim. Thus merges and links between roots change only identity rows.
- **`pending_matches` links two book rows.** For a match of only the tags, the found book is a normal book that the user can play. The application also keeps a pending row. When the user accepts the match, the merge operation runs. When the user refuses it, the application deletes the pending row.
- **Position model**: one offset in seconds for all of the book. The application uses the durations in `book_files` to find the file and the offset in it. Thus a new track order or a new encoding of a book changes only the cache, never the state.

We also examined a `listening_state` table with the key `(book_id, origin)` and an "active" flag, in place of a separate `state_conflicts` table. We did not use it, because each read of the normal case must then filter the rows. With a separate table, `listening_state` has one row for each book, and conflicts are the exception.

### Book detection (leaf-folder rule)

```
  for each folder F under the root (not excluded, symlinks not followed):
    audio directly in F?
      yes, no subfolder contains audio   --> F is a book
      yes, a subfolder contains audio    --> warning mixed-files-and-folders
      no, all subfolders are disc folders
          (CD|Disc|Part + number) w/ audio --> F is a book (discs in natural order)
      no, some disc and some non-disc     --> warning invalid-disc-layout
      no                                  --> F is a group; recurse
  no audio anywhere below F                --> ignored silently
  audio directly in the root               --> warning audio-in-root (per file)
  leaf_mode = file                         --> every audio file is one book
```

- The application finds audio files by their extension, in upper case or lower case: `m4b m4a mp3 opus ogg flac wav aac wma`. Sometimes the tag reader cannot open a file with one of these extensions. Then the application writes the warning `unreadable-audio`, and the file is not a track of the book.
- The check for `multiple-albums-in-book` runs in `folder` mode after the application reads the tags. It writes a warning, but it does not divide the book.

We also examined two other models. The first model was templates with a fixed depth. We did not use it for the reasons in "Context". The second model was templates with optional segments. We did not use it, because the result is not clear. For example, `Author/X/Y` can be a series with a book, or a book with a subfolder. The leaf-folder rule finds the answer from the files.

### Metadata from name patterns

- The tags come first. The title comes from `album`. The author comes from `albumartist`, then `artist`, then `composer`. An empty value, or a value with only spaces, is not a value.
- The pattern fills only the fields that have no value. The application records `source = path` for these fields.
  - Hierarchy `{author}/…/{title}`: the author is the first folder in the root, if the book is at depth 2 or more. The title is the name of the book. The application ignores the folders between them.
  - Name `{author} - {title}`: the application divides the name of the book at the first ` - `. The name of the book is the folder name, or the file name without the extension in `file` mode. A `-` without spaces does not divide the name, so a name such as `Jean-Luc` stays together.
- If the pattern does not agree with the path, the title is the name of the book. The application writes no warning.

### Setup scores

```
  pick folder --> nesting/outside checks --> discovery scan (no writes)
       --> sample <= 50 books, spread across first-level folders
       --> read tags of sampled books
       --> score: each leaf_mode x each name_pattern
              pattern score  = share of sampled tagged books where the
                               path-derived author/title fuzzily agrees with tags
              leaf_mode hint = share of leaf folders with >1 distinct album
       --> preview (recommended choice + 5 sample books per choice)
       --> confirm: root, settings and full scan applied in one transaction
```

- To compare a path value with a tag, the application uses the standard form of the `tags` claims. This form is lower case, with no punctuation and one space between words. It also accepts a value that contains all the words of the other value. Thus `Terry Pratchett & Stephen Baxter` agrees with `Terry Pratchett`. Initials, for example `J.R.R.` and `John Ronald Reuel`, give a weak agreement. One pure function contains the exact limits.
- The scores run only at setup and when the user edits the settings. They do not run during a normal rescan. Thus the metadata that the application shows does not change when the user adds books.
- The same discovery scan gives the preview for a new root path and the moved-root recommendation. The application gives the moved-root recommendation when half or more of the known `rel_path` values of an unreachable root exist in the new folder.

We also examined a model that selects the pattern automatically at each scan, for each part of the tree. We did not use it in the MVP for two reasons. First, the result can change when the user adds books. Second, it helps only parts of the tree that have some tags and not others. The section "Later investigations" records it.

### Scanning as a pure function

```
  FileSystemPort.walk(root) --> [entries]            (platform adapter, lstat only)
                                    |
        leaf_mode + exclusions ---> | detect_books()     (pure core)
                                    v
                         books_found + warnings
                                    |
        TagReaderPort (stale only) -> metadata + fallback from name_pattern
                                    |
        known identities ---------> | resolve_identity()  (pure core)
                                    v
               linked | new | pending_tag_match | missing | unavailable
                                    |
                     LibraryStore.apply(result)     (single transaction)
```

- `detect_books` receives simple entries (path, kind: file|dir|symlink, size, mtime). It gives books and warnings. Tests use trees in memory.
- The application reads tags only for books with an old cache entry (the size or the mtime changed).
- The application applies the results in **one transaction for each root scan**. If the application stops during a scan, the previous state does not change. Position saves from playback use the same writer connection. Thus they wait until the transaction is complete, and they do not fail.

### Identity resolution

```
  found book (in root R)
    |
    +-- abs_path match -----------------------------------> same book
    +-- rel_path match, known book in R ------------------> same book, update abs_path
    +-- rel_path match, other root, old location GONE ----> same book, update claims
    +-- tags match, old location GONE --------------------> new book + pending match
    +-- otherwise ----------------------------------------> new book

  GONE(old)  :=  old root declared gone
             OR (old root reachable AND old path does not exist)

  known books of R not found ----------------> missing
  known books of an unreachable root --------> unavailable (until reachable or declared gone)
```

- The `tags` claim keeps the author and the title in a standard form: lower case, one space between words, and no punctuation. Different books can have the same `album` value (for example, collections). Thus a match of only the tags always needs the agreement of the user.
- The checks for reachable roots and for paths use `FileSystemPort`. Thus tests can do these checks.

### Merge operation

```
  merge(keep, absorb):          (one transaction)
    book_identities: absorb's rows re-pointed to keep
    state:
      neither played   -> nothing
      one played       -> that state becomes keep's state
      both played      -> keep's state stays; absorb's state -> state_conflicts
                          (plus any conflicts absorb already had)
    pending_matches referencing absorb -> re-pointed or dropped if now self-referencing
    absorb: deleted
```

- Two operations start a merge. The first is when the user accepts a tag match. The second is when the user says that a root is gone. Then the application merges books with the same `rel_path` automatically, and keeps matches of only the tags as `pending_matches`.
- "Played" means that `last_played` has a value.
- When the user selects a state in a conflict (`ui/library`), one transaction moves the selected row into `listening_state` and deletes the other rows.

### Roots

- A root is unreachable when its path does not exist or is not a readable directory at the time of the scan. Its books become `unavailable`, and nothing else about them changes.
- **Root is gone**: the application deletes the root row, its exclusions and its warnings, and marks its books as `missing`. Then the merge operation runs. The application refuses this operation for the last root.
- **Change path**: the application does the nesting check and the check for a reachable path. Then it shows the discovery preview (the found books and the known books). Then it changes `roots.path` and scans the root again. The `rel_path` match in the same root links the books again.
- **Outside the roots**: one core function, `root_for(path) -> Root | None`, compares the path with the root paths. Each operation that receives a path from the user goes through this function, for example drag and drop or a future CLI argument. If the result is `None`, the operation stops.

### Start and storage safety

```
  db file absent ............................ first run (setup)
  user_version < current .................... copy to <name>.bak-v<old>, migrate in
                                              one transaction, normal start
  user_version > current .................... storage failure screen (no writes)
  cannot open / integrity_check fails ....... storage failure screen (no writes)
       "Start a new library" -> rename to <name>.broken-<timestamp>, then setup
```

- `PRAGMA user_version` contains the schema version. Each migration runs in one transaction. If the migration fails, the transaction stops and the database does not change. The `.bak-v<old>` copy gives more safety.
- The database is in `platformdirs.user_data_dir("abookie")`.

### UI

- View-models:
  - `SetupViewModel`: discovery, scores and preview. The first start, a new root and a new root path use it.
  - `LibraryViewModel`: the book list, with the most recent `last_played` first. This includes books with a conflict.
  - `RootsViewModel`: add a root, change the path, change the settings, tell the application that a root is gone, and start a rescan.
  - `WarningsViewModel`, `MatchConfirmationViewModel`, `StateConflictViewModel` and `StorageFailureViewModel`.
- Views use only these view-models.
- "Open location" uses `QDesktopServices.openUrl` through a platform port. Thus tests can examine it.

## Risks / Trade-offs

- [A full scan of a large library is slow, mostly on a NAS.] → The application reads tags only for books with an old cache entry. Setup uses a sample of limited size. Scans run outside the UI thread and show their progress. File monitoring is for a later change.
- [In `folder` mode, a flat folder of single-file books becomes one book with many parts] → The warning `multiple-albums-in-book` shows this problem. Setup recommends `file` mode when the sample shows it.
- [A root can contain folders of single-file books and folders of multi-file books. One leaf mode does not agree with both.] → In the MVP, the user divides them into different roots or accepts the warnings. Settings for each folder are a later investigation.
- [The scores recommend the wrong pattern] → It is only a recommendation with a preview. Also, the pattern changes only fields that have no tag value.
- [The application does not follow symbolic links. Thus it does not find books in a library that is made of symbolic links.] → The warning log shows each symbolic link that the application did not follow. Symbolic links are a later investigation.
- [Two roots have the same `rel_path`, for example `Unknown/Untitled`] → The application links books between roots only when the old location is gone. In other cases, it makes a different book.
- [The standard form of tags merges different editions] → A match of only the tags always needs the agreement of the user. The UI shows the duration, so the user can see the difference.
- [Many conflicts between states stay open] → Each conflict only adds one indicator in the list, and it stops no operation. To correct a conflict, the user selects one state the next time the user plays the book.

## Migration Plan

This is a new database, so no migration is necessary. The application makes schema version 1 on the first start.

## Open Questions

- The UI for the scan progress (in the library or in a dialog). This has no effect on the specs.
- The limits for the comparison of path values and tags, and the size of the setup sample. These are values in one pure function. We will set them during the implementation, with fixture trees.

## Later investigations (out of scope, recorded for follow-up changes)

- **Content fingerprints**: an algorithm that stays the same when tags change. For example, a hash of the audio frames that skips the tag atoms.
- **Audio outside the roots**: accept it with fewer claims, offer to add a root, or continue to refuse it.
- **Name patterns that the user writes**: for example `{series} {index} - {title}`, with a check and a preview in the UI.
- **Settings for each folder**: a leaf mode and a name pattern for each part of the tree. The same scores can possibly recommend them.
- **Symbolic links**: logical paths, loop detection by device and inode, and the handling of duplicates.
- **File monitoring**: inotify on Linux, with an abstraction for other operating systems.
