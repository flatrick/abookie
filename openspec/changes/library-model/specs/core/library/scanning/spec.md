# Spec Delta

## Purpose

Defines how books are discovered from a library root, and how content that does not fit the root's structure is reported to the user and resolved.

## ADDED Requirements

### Requirement: Scans run on add and on request
The system SHALL scan a root when it is added, when its structure changes, and when the user requests a rescan; it SHALL NOT watch the filesystem for changes.

#### Scenario: Root added
- **WHEN** the user adds a root
- **THEN** the root is scanned and its books appear in the library

#### Scenario: Files added after the last scan
- **GIVEN** a scanned root
- **WHEN** a new book folder is copied into it and the user does not rescan
- **THEN** the library does not show the new book until the next scan

### Requirement: Scanning never modifies user files
Scanning and every other library operation SHALL NOT create, move, rename, modify or delete any file under a library root.

#### Scenario: Scan of a root with mismatches
- **GIVEN** a root containing files that do not match its structure
- **WHEN** the root is scanned
- **THEN** every file under the root is byte-for-byte and name-for-name unchanged afterward

### Requirement: Mismatches are logged with reason codes
Each audio file or folder that cannot be placed into a book SHALL produce a warning in the root's warning log containing its path relative to the root and a reason code from a fixed set.

#### Scenario: Audio at the wrong depth
- **GIVEN** a root with template `{author}/{title}`, leaf type `folder`
- **WHEN** the root contains `stray.mp3` directly in the root
- **THEN** a warning with reason `audio-at-wrong-depth` and path `stray.mp3` is logged

#### Scenario: Reason code set
- **WHEN** any warning is logged
- **THEN** its reason is one of `audio-at-wrong-depth`, `mixed-files-and-folders`, `empty-book-folder`, `unreadable-audio`, or `invalid-disc-layout`

### Requirement: Warning log persists until the next scan
The warning log of a root SHALL be stored persistently and SHALL be replaced as a whole by the results of that root's next scan.

#### Scenario: Restart keeps warnings
- **GIVEN** a root whose last scan logged warnings
- **WHEN** the application is restarted
- **THEN** the same warnings are shown

#### Scenario: Resolved mismatch disappears
- **GIVEN** a warning for `stray.mp3`
- **WHEN** the user moves the file into a valid book folder and rescans
- **THEN** the warning no longer appears

### Requirement: Paths can be excluded per root
The user SHALL be able to exclude an exact path relative to a root from that root's library; excluded paths and everything beneath them are skipped by scans and produce no warnings.

#### Scenario: Excluding a warned path
- **GIVEN** a warning for `Extras/` in a root
- **WHEN** the user excludes `Extras/` and rescans
- **THEN** no books or warnings are produced from `Extras/` or anything beneath it

#### Scenario: Stale exclusion
- **GIVEN** an exclusion for `Extras/` in a root
- **WHEN** a rescan finds that `Extras/` no longer exists
- **THEN** the exclusion is removed and the user is notified
