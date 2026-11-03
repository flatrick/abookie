# Spec Delta

## Purpose

Defines the library as a set of root folders that contain the audiobook collections of the user. Each book that the application knows is in one of these roots.

## ADDED Requirements

### Requirement: Library has at least one root
The library MUST always contain one root folder or more. The system MUST refuse to remove the last root.

#### Scenario: First start needs a root
- **GIVEN** a library with no roots
- **WHEN** the application starts
- **THEN** the user must add a root before the user can use the library

#### Scenario: System refuses to remove the last root
- **GIVEN** a library with only one root
- **WHEN** the user tries to remove that root
- **THEN** the system refuses, tells the user why, and keeps the root

### Requirement: A root is not in a different root
The system MUST refuse a new root path that is in a different root or that contains a different root. This applies when the user adds or moves a root. The system compares the fully resolved paths.

#### Scenario: Root in an existing root
- **GIVEN** a root `/data/books`
- **WHEN** the user adds `/data/books/scifi`
- **THEN** the system refuses, and the reason gives the name of the existing root

#### Scenario: Root that contains an existing root
- **GIVEN** a root `/data/books/scifi`
- **WHEN** the user adds `/data/books`
- **THEN** the system refuses, and the reason gives the name of the existing root

#### Scenario: Symbolic link to a folder in an existing root
- **GIVEN** a root `/data/books` and a symbolic link `/home/u/b` that points to `/data/books/scifi`
- **WHEN** the user adds `/home/u/b`
- **THEN** the system refuses, because the root is nested

### Requirement: System keeps the root path as the user wrote it
The system MUST keep the path of each root as the user wrote it, and MUST NOT resolve symbolic links in it. The system MUST make the absolute paths of the books from this path.

#### Scenario: Root path that is a symbolic link
- **GIVEN** `/home/u/Audiobooks` is a symbolic link to `/mnt/nas/books`
- **WHEN** the user adds `/home/u/Audiobooks` as a root, and the root contains `Author A/Book B`
- **THEN** the root path is `/home/u/Audiobooks`, and the absolute path of the book is `/home/u/Audiobooks/Author A/Book B`

### Requirement: Unreachable roots keep their books
The system MUST mark the books of an unreachable root as unavailable. The books and their listening state MUST stay until the root is reachable again. They also stay until the user says that the root is gone.

#### Scenario: Network share offline
- **GIVEN** a root on a network share, with books that have saved positions
- **WHEN** the share is not mounted and the library shows
- **THEN** the library shows these books as unavailable, with their saved positions

#### Scenario: Root becomes reachable again
- **GIVEN** books that are unavailable because their root was unreachable
- **WHEN** the root is reachable again and the system scans it
- **THEN** the books are available again, and their listening state did not change

### Requirement: User can tell the system that a root is gone
The user MUST be able to tell the system that a root is gone. Then the system removes the root and marks its books as missing, and it keeps their listening state.

#### Scenario: Network share removed permanently
- **GIVEN** an unreachable root with books that have saved positions, and one other root or more
- **WHEN** the user tells the system that the unreachable root is gone
- **THEN** the system removes the root, and shows its books as missing with their saved positions. The system can merge these books as book identity tells.

### Requirement: User can change the path of a root
The user MUST be able to change the path of a root and keep the settings, exclusions and books of that root. Before the user accepts, the system MUST show how many known books of the root are at the new path.

#### Scenario: Share mounted at a new location
- **GIVEN** a root `/mnt/nas/books` with 230 known books, and the root is unreachable
- **WHEN** the user changes its path to `/media/nas/books`, and the preview shows that the system found 212 of 230 books
- **THEN** after the user accepts, the root keeps its settings and exclusions, and the system scans it. The 212 books keep their identity and listening state.

#### Scenario: New path is unreachable
- **WHEN** the user changes the path of a root to a location that does not exist or that is not a readable folder
- **THEN** the system refuses, and the root does not change

### Requirement: System recommends a path change for a moved root
When the user adds a root and a different root is unreachable, the system MUST compare the books of the two roots by their paths. If most of them are the same, the system MUST offer to change the path of that root.

#### Scenario: User adds a moved network share as a new root
- **GIVEN** an unreachable root `/mnt/nas/books`, and most of its books are at the same paths under `/media/nas/books`
- **WHEN** the user adds `/media/nas/books` as a new root
- **THEN** the system asks if `/mnt/nas/books` moved there. If the user accepts, the system changes the path of that root. If the user does not accept, the system adds a new root.

### Requirement: System refuses audio outside all roots
The system MUST refuse to add or play audio that is outside all library roots. The system MUST tell the user that the location is not in a library root, and how to add a root.

#### Scenario: User opens a file outside all roots
- **GIVEN** only the root `/data/books`
- **WHEN** the user tries to open `/home/u/Downloads/book.m4b`
- **THEN** the system refuses and tells the user that the file is outside all library roots. It also tells the user where to add a root in the settings.
