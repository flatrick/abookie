# Spec Delta

## Purpose

Defines how a library root declares the on-disk layout of its books, so that the system knows deterministically where each book begins and ends.

## ADDED Requirements

### Requirement: Each root has exactly one structure
Every library root SHALL have exactly one structure, chosen by the user when the root is added and changeable later.

#### Scenario: Adding a root requires a structure
- **WHEN** the user adds a root
- **THEN** the user must choose one of the available structures before the root is saved

#### Scenario: Changing a root's structure
- **GIVEN** a root with structure "Author / Book"
- **WHEN** the user changes it to "Author / Series / Book"
- **THEN** the new structure is saved and the root is rescanned

### Requirement: Structures are presets expressed as templates
The system SHALL offer a fixed set of structure presets, and SHALL store each root's structure as a path template plus leaf type, never as a preset identifier only.

#### Scenario: Available presets
- **WHEN** the user chooses a structure
- **THEN** the options are: "One file per book" (`{title}`, file), "Author / Book" (`{author}/{title}`, folder), "Author / Series / Book" (`{author}/{series}/{title}`, folder), and "Author / Book file" (`{author}/{title}`, file)

#### Scenario: Stored as template
- **WHEN** a root with preset "Author / Series / Book" is saved
- **THEN** its stored structure is the template `{author}/{series}/{title}` with leaf type `folder`

### Requirement: Templates match strictly by depth
A template SHALL match a book only at exactly the depth given by its number of segments below the root; templates have no optional segments.

#### Scenario: Book at the template's depth
- **GIVEN** a root with template `{author}/{series}/{title}` and leaf type `folder`
- **WHEN** the root contains `Author A/Series S/Book B/01.mp3`
- **THEN** `Author A/Series S/Book B` is a book

#### Scenario: Book at the wrong depth
- **GIVEN** a root with template `{author}/{series}/{title}` and leaf type `folder`
- **WHEN** the root contains `Author A/Book C/01.mp3`
- **THEN** no book is derived from it and a warning is logged for it

### Requirement: File leaf type
For leaf type `file`, the system SHALL treat each audio file at the template's depth as one book.

#### Scenario: Single-file books
- **GIVEN** a root with template `{author}/{title}` and leaf type `file`
- **WHEN** the root contains `Author A/Book One.m4b` and `Author A/Book Two.m4b`
- **THEN** two books are derived, one per file

### Requirement: Folder leaf type
For leaf type `folder`, the system SHALL treat each folder at the template's depth as one book whose audio files play in natural sort order.

#### Scenario: Natural sort of tracks
- **GIVEN** a book folder containing `1.mp3`, `2.mp3` and `10.mp3`
- **WHEN** the book's track order is determined
- **THEN** the order is `1.mp3`, `2.mp3`, `10.mp3`

### Requirement: Disc subfolders in folder books
A folder book SHALL accept disc subfolders only when it contains no loose audio files and every subfolder name matches a disc pattern (CD, Disc or Part followed by a number); discs play in natural order.

#### Scenario: Book split into discs
- **GIVEN** a book folder containing only `CD1/` and `CD2/`, each with audio files
- **WHEN** the book's track order is determined
- **THEN** all tracks of `CD1` come before all tracks of `CD2`, each disc in natural order

#### Scenario: Loose files mixed with disc folders
- **GIVEN** a book folder containing `intro.mp3` and `CD1/`
- **WHEN** the root is scanned
- **THEN** no book is derived from that folder and a warning is logged for it

### Requirement: Non-audio files are ignored
The system SHALL ignore non-audio files inside book folders without logging warnings, and SHALL use a file named `cover` or `folder` with an image extension as the book's cover art.

#### Scenario: Cover image and metadata files
- **GIVEN** a book folder containing `01.mp3`, `cover.jpg` and `info.nfo`
- **WHEN** the root is scanned
- **THEN** one book is derived with `cover.jpg` as its cover art and no warnings are logged

### Requirement: Template segments provide fallback metadata
Path segments matched by named template placeholders SHALL be used as metadata values when the corresponding tag is missing, and the stored metadata SHALL record whether each value came from tags or from the path.

#### Scenario: Missing author tag
- **GIVEN** template `{author}/{title}` and a book at `Jane Doe/Some Book` whose files have no author tag
- **WHEN** the book's metadata is read
- **THEN** the author is "Jane Doe" with its source recorded as path
