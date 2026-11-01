# Spec Delta

## Purpose

Defines how a book is recognized as the same book across scans, so that listening state stays attached to it when its files are moved or renamed.

## ADDED Requirements

### Requirement: Books carry identity claims
Each book SHALL have a set of identity claims, each with a kind and a value, and the set of claim kinds SHALL be extensible without changing existing claims.

#### Scenario: Claims recorded for a new book
- **GIVEN** a root `/data/books` and a new book at `/data/books/Author A/Book B`
- **WHEN** the book is first discovered
- **THEN** it has an `abs_path` claim `/data/books/Author A/Book B`, a `rel_path` claim `Author A/Book B`, and a `tags` claim when author and title tags are present

#### Scenario: Unknown future claim kind
- **GIVEN** a stored claim of a kind the current version does not use
- **WHEN** identity matching runs
- **THEN** the claim is kept unchanged and ignored by matching

### Requirement: MVP claim kinds
In the MVP the system SHALL create and match only the claim kinds `abs_path` (fully resolved absolute path), `rel_path` (path relative to its root) and `tags` (normalized author and title).

#### Scenario: Book without author or title tags
- **WHEN** a book whose tags lack author or title is discovered
- **THEN** it receives `abs_path` and `rel_path` claims and no `tags` claim

### Requirement: Claims are matched in a fixed order
When a scan finds a book, the system SHALL match it against known books by `abs_path` first, then `rel_path`, then `tags`, and the first kind that produces a match SHALL decide the outcome.

#### Scenario: Same location
- **WHEN** a scan finds a book whose resolved path equals a known book's `abs_path` claim
- **THEN** it is the same book

#### Scenario: Root relocated
- **GIVEN** a known book with claim `rel_path` = `Author A/Book B` under root `/mnt/nas/books`
- **WHEN** the root is now mounted at `/media/nas/books` and the scan finds `Author A/Book B` with no `abs_path` match
- **THEN** it is the same book and its `abs_path` claim is updated

#### Scenario: Book moved between roots
- **GIVEN** a known book with `rel_path` `Author A/Book B` in root 1 whose old location no longer exists
- **WHEN** a scan of root 2 finds `Author A/Book B`
- **THEN** it is the same book and its path claims are updated

### Requirement: Path matches link only books whose old location is gone
A `rel_path` or `tags` match SHALL only link to a known book whose previously claimed absolute path no longer exists; otherwise the found book is treated as a separate book.

#### Scenario: Two copies present
- **GIVEN** a known book at `/data/a/Author A/Book B` that still exists
- **WHEN** a scan of another root finds `Author A/Book B`
- **THEN** the found book is a new, separate book

### Requirement: Tag matches require user confirmation
A match made only by the `tags` claim SHALL NOT be linked automatically; the system SHALL ask the user to confirm, showing both books' paths, total durations and saved positions.

#### Scenario: User confirms a tag match
- **GIVEN** a known book with `tags` claim author "Jane Doe" and title "Some Book" whose old path is gone
- **WHEN** a scan finds a renamed folder with the same tags and the user confirms
- **THEN** the found book is linked to the known book and keeps its listening state

#### Scenario: User rejects a tag match
- **WHEN** the user rejects a proposed tag match
- **THEN** the found book is added as a new book and the known book is unchanged

### Requirement: Missing books are kept
A known book that no scan matches SHALL be kept and shown as missing, together with its listening state, and SHALL NOT be deleted automatically.

#### Scenario: Book deleted from disk
- **GIVEN** a known book with a saved position
- **WHEN** its files are deleted and its root is rescanned
- **THEN** the book is shown as missing with its saved position, until the user removes it
