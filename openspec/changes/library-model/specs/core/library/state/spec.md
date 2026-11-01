# Spec Delta

## Purpose

Separates the data derived from audio files, which can be rebuilt at any time, from the listening state created by the user, which must never be lost silently.

## ADDED Requirements

### Requirement: Metadata cache is disposable
The system SHALL keep book metadata (title, author, narrator, series, duration, chapters, cover) in a cache that can be fully cleared and rebuilt from the files without affecting listening state.

#### Scenario: Cache rebuilt
- **GIVEN** books with saved positions
- **WHEN** the metadata cache is cleared and the roots are rescanned
- **THEN** metadata is restored from the files and every saved position is unchanged

### Requirement: Cache entries are invalidated by file changes
The system SHALL refresh a book's cached metadata during a scan when any of its audio files' size or modification time differs from what was cached.

#### Scenario: File re-tagged
- **GIVEN** a cached book whose title tag is then edited on disk
- **WHEN** its root is rescanned
- **THEN** the cached title reflects the new tag

### Requirement: Listening state is durable
The system SHALL persist each book's listening state (position, playback speed, last played time, finished flag) and SHALL NOT discard it except on an explicit user action.

#### Scenario: Switching between books
- **GIVEN** book A paused at 2h10m and book B paused at 35m
- **WHEN** the user plays book B, then returns to book A
- **THEN** book A resumes at 2h10m and book B's position is saved where it stopped

#### Scenario: Application restart
- **GIVEN** a book being played
- **WHEN** the application is closed and reopened
- **THEN** the book's saved position is within the periodic save interval of where playback was

### Requirement: Listening state survives storage failures
If the stored data cannot be read or migrated, the system SHALL NOT overwrite or delete it; it SHALL report the problem and keep a backup of the existing data.

#### Scenario: Schema migration fails
- **GIVEN** an existing database from an older version
- **WHEN** migrating it to the current schema fails
- **THEN** the original database file is preserved unchanged and the user is told what happened
