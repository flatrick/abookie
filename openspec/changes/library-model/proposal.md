# Proposal

## Why

An audiobook player must keep the listening position of each book, not only of the current book. Then the user can change from one book to a different book at any time. For this, the player needs a library model. The model tells where books are, what a book is, and how to find a book again after its files move. It also tells how to keep listening state safe. Resume, the book list and chapters all use this model, so it must come before the playback features.

## What Changes

- **Library roots**: The library is a list of one or more root folders. A root cannot be in a different root. The library always has one root or more. The application asks for the first root on the first start. The application keeps each root path as the user wrote it. The user can change the path of a root (relocation). The user can also tell the application that a root is gone. If a new root looks like an unreachable root that moved, the application tells the user to change the path of that root.
- **Book detection**: The application finds books from the folders that contain audio, not from templates with a fixed depth. A folder that contains audio files is a book. A folder that contains only folders is a group (for example, an author, a series or an anthology). A folder that contains only disc folders is one book. The depth is not important. Each root has a leaf mode: `folder` (the default) or `file`. In `file` mode, each audio file is a book.
- **Metadata from paths**: Tags are the primary source of metadata. Each root has a name pattern. The application uses the pattern only to fill a field that the tags do not give. There are two built-in patterns: folder hierarchy (`{author}/…/{title}`) and folder or file name (`{author} - {title}`). The application keeps patterns as text. Thus, a later change can add patterns that the user writes, with no change to the data model.
- **Setup with a recommendation**: When the user adds a root, the application scans a sample of the books in it. It compares each leaf mode and each name pattern with the tags of these books. Then it shows the best result and a preview. The user accepts the recommendation or selects a different one. After setup, the result of each scan is always the same for the same files.
- **Scanning**: The application scans a root when the user adds it, when its settings change, and when the user starts a rescan. The application does not monitor files for changes. In the MVP, the application does not follow symbolic links in a root.
- **Warning log**: Sometimes the application cannot put content into a book. Then it writes a warning with a reason code in the log of that root. To correct a warning, the user changes the settings of the root, moves the files, or excludes the path. The application never moves or renames the files of the user.
- **Book identity**: Each book has a set of identity claims in a table that can hold new kinds of claims. The MVP uses three kinds: the absolute path, the path in the root, and the tags. The application compares them in this sequence. In one root, a match of the path in the root is always correct. Between two roots, the application links a book only when its old location is gone. A book in an unreachable root stays unavailable until the user tells the application that the root is gone. Before the application links a book only by its tags, it always asks the user. A later investigation will examine content fingerprints.
- **Merge of books**: When the application links two books that it knows already, it does one merge operation. The user can tell the application that a root is gone. Then the application merges each book of that root with a book that has the same path in a different root. If the user played both books, the application keeps both listening states. The next time the user plays the book, the user selects one state.
- **Cache and listening state**: The application can delete the metadata cache (tags, duration, chapters, cover) and make it again. The application never loses listening state (position, speed, last played time, finished flag) without the user knowing.
- **Safe start**: The application starts the first-run setup only when the library database does not exist. The application never writes over a database that it cannot read, or a database that has a newer schema. The user can stop the application, or start a new library. A new library renames the old file. It does not delete it.
- **Audio outside the roots**: In the MVP, the application refuses audio that is outside all roots, and it tells the user why. A later investigation will examine how to support these files.
- **UI**: The UI has these parts:
  - Setup with a preview, on the first start and when the user adds a root.
  - Root management: change the path, tell the application that a root is gone, change the settings, and start a rescan.
  - The warning log.
  - A book list that shows the progress, with the last played book first.
  - Confirmation of tag matches.
  - A selection between two listening states when the user plays a book.

## Capabilities

### New Capabilities
- `core/library`: Library roots. There is one root or more, and roots are not nested. Also: the root path as the user wrote it, relocation, a root that is gone, the moved-root recommendation, unreachable roots, and audio outside all roots.
- `core/library/structures`: Book detection from folders, leaf modes, disc folders, audio file types, name patterns for missing metadata, and the setup recommendation from tags.
- `core/library/scanning`: When scans start, the warning log with reason codes, symbolic links, and exclusions for each root.
- `core/library/identity`: The table of identity claims, the MVP claim kinds, and the sequence of the comparison. Also: when a location is gone, the merge of books, and the confirmation of tag matches.
- `core/library/state`: The metadata cache that the application can delete, and the listening state that it must keep. Also: conflicts between listening states, and a safe start when the data is not usable.
- `ui/library`: Root setup with a preview, root management, the warning log and the book list. Also: the confirmation of tag matches, and the selection between listening states.

### Modified Capabilities
<!-- none: depends on project-foundation's core/ui/platform cross-cutting specs, which are unchanged -->

## Impact

- This change depends on `project-foundation` (layers, ports, TDD rules).
- New core modules: library roots, book detection, name patterns and scores, scanning, identity and merge, and state.
- New ports: filesystem access, tag reading, persistence, and a port that opens a location in the file manager.
- New platform adapters: the filesystem, mutagen and SQLite.
- New SQLite schema: roots, exclusions, warnings, books, book identities, metadata cache, book files, chapters, listening state, state conflicts, and pending tag matches.
- New UI: the setup with a preview, library settings, the warning log, the book list, match confirmation, and the selection between listening states.
- Investigations for later: content fingerprints, audio outside the roots, name patterns that the user writes, settings for each folder, symbolic links, and file monitoring.
