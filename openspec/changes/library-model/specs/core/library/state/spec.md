# Spec Delta

## Purpose

Keeps two types of data apart. The system can make the data from the audio files again at any time. The user makes the listening state, and the system must never lose it without the user knowing. This is also true when books merge or when the system cannot read the stored data.

## ADDED Requirements

### Requirement: System can delete the metadata cache
The system MUST keep the metadata of books (title, author, narrator, series, duration, chapters, cover) in a cache. The system can delete all of the cache and make it again from the files, with no change to the listening state.

#### Scenario: System makes the cache again
- **GIVEN** books with saved positions
- **WHEN** the system deletes the metadata cache and scans the roots again
- **THEN** the system reads the metadata from the files again, and each saved position is the same as before

### Requirement: System reads metadata again after a file change
During a scan, the system MUST read the metadata of a book again if the size or modification time of a file changed.

#### Scenario: User changes a tag
- **GIVEN** a book in the cache, and the user then edits its album tag on the disk
- **WHEN** the system scans its root again
- **THEN** the title in the cache is the new tag

### Requirement: System keeps the listening state
The system MUST keep the listening state of each book (position, playback speed, last played time, finished flag). The system MUST NOT delete it, except when the user tells it to.

#### Scenario: User changes between books
- **GIVEN** book A saved at 2h10m and book B saved at 35m
- **WHEN** the user selects book B, and then selects book A again
- **THEN** the saved position of book A is 2h10m, and the saved position of book B is 35m

#### Scenario: Application starts again
- **GIVEN** a book with the saved position 1h05m
- **WHEN** the user stops the application and starts it again
- **THEN** the saved position of the book is 1h05m

### Requirement: A merge keeps two listening states as a conflict
When two books merge and the user played both books, the system MUST keep both listening states as a conflict on the merged book. When the user played only one book, its state MUST become the state of the merged book, with no conflict.

#### Scenario: User played both books
- **GIVEN** book A, last played in March at 4h12m, and book B, last played today at 20m
- **WHEN** the system merges A and B
- **THEN** the merged book has both states as a conflict, and the system deletes neither state

#### Scenario: User played only one book
- **GIVEN** book A saved at 4h12m, and book B that the user never played
- **WHEN** the system merges A and B
- **THEN** the state of the merged book is 4h12m, and there is no conflict

### Requirement: Only the user selects the state in a conflict
A conflict between listening states MUST stay until the user selects one state. Then the selected state becomes the state of the book, and the system deletes the other states.

#### Scenario: User selects a state
- **GIVEN** a book with the two states 4h12m at 1.0x and 20m at 1.5x
- **WHEN** the user selects the state 4h12m
- **THEN** the state of the book is 4h12m at 1.0x, and there is no conflict

#### Scenario: User does not select a state
- **GIVEN** a book with a conflict between states
- **WHEN** the application starts again many times and the user does not select a state
- **THEN** the system keeps all the states

### Requirement: First start only when the database does not exist
The system MUST start the first-run setup only when no library database exists. It MUST NOT start it because the stored library has no roots or because the system cannot read the library.

#### Scenario: Database does not exist
- **GIVEN** no library database exists
- **WHEN** the application starts
- **THEN** the application shows the first-run root setup

### Requirement: Storage failures do not change the stored data
The system MUST NOT change or delete stored data that it cannot read or migrate, or that has a newer schema than the application. The system MUST tell the user about the problem and the location of the data.

#### Scenario: Schema migration fails
- **GIVEN** a database from an older version
- **WHEN** the migration to the current schema fails
- **THEN** the original database file does not change, and the system tells the user what occurred

#### Scenario: Database from a newer version
- **GIVEN** a database from a newer version of the application
- **WHEN** an older version starts
- **THEN** the database does not change, and the system tells the user that a newer version made it

#### Scenario: Database that the system cannot read
- **GIVEN** a database file that the system cannot read
- **WHEN** the application starts
- **THEN** the file does not change, and the system lets the user stop the application or start a new library

### Requirement: A new library keeps the old database file
When the user starts a new library after a storage failure, the system MUST add the suffix `.broken-<timestamp>` to the name of the existing database. It MUST NOT delete the database. Then the system starts the first-run setup.

#### Scenario: User starts a new library
- **GIVEN** a corrupt database `library.db`
- **WHEN** the user starts a new library
- **THEN** the name of the file changes to `library.db.broken-<timestamp>`, and the application shows the first-run setup

### Requirement: System makes a copy before a migration
Before the system migrates the stored data to a newer schema, it MUST make a copy of the data. The migration MUST NOT change the copy.

#### Scenario: Migration completes
- **GIVEN** a database with the schema version 1
- **WHEN** the application migrates it to version 2
- **THEN** a copy of the version 1 database is in the same folder after the migration
