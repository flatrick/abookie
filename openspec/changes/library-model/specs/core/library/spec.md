# Spec Delta

## Purpose

Defines the library as a set of root folders holding the user's audiobook collections. Every book the application knows about lives under one of these roots.

## ADDED Requirements

### Requirement: Library has at least one root
The library SHALL always contain at least one root folder, and the system SHALL refuse to remove the last remaining root.

#### Scenario: First run requires a root
- **GIVEN** a library with no roots
- **WHEN** the application starts
- **THEN** the user is required to add a root before the library can be used

#### Scenario: Removing the last root is refused
- **GIVEN** a library with exactly one root
- **WHEN** the user tries to remove that root
- **THEN** the removal is refused with an explanation and the root remains

### Requirement: Roots are not nested
The system SHALL reject adding a root that is inside, or contains, an existing root, comparing fully resolved paths.

#### Scenario: Root inside an existing root
- **GIVEN** a root `/data/books`
- **WHEN** the user adds `/data/books/scifi`
- **THEN** the addition is rejected and the reason names the existing root

#### Scenario: Root containing an existing root
- **GIVEN** a root `/data/books/scifi`
- **WHEN** the user adds `/data/books`
- **THEN** the addition is rejected and the reason names the existing root

#### Scenario: Symlinked path resolving into an existing root
- **GIVEN** a root `/data/books` and a symlink `/home/u/b` pointing to `/data/books/scifi`
- **WHEN** the user adds `/home/u/b`
- **THEN** the addition is rejected as nested

### Requirement: Unreachable roots keep their books
The system SHALL mark the books of an unreachable root as unavailable and SHALL NOT delete those books or their listening state.

#### Scenario: Network share offline
- **GIVEN** a root on a network share with books that have saved positions
- **WHEN** the share is not mounted and the library is shown
- **THEN** those books are shown as unavailable with their saved positions intact

#### Scenario: Root becomes reachable again
- **GIVEN** books marked unavailable because their root was unreachable
- **WHEN** the root becomes reachable and is rescanned
- **THEN** the books are available again with their listening state unchanged

### Requirement: Audio outside every root is refused
The system SHALL refuse to add or play audio located outside every library root, and SHALL tell the user that the location is not in any library root and how to add one.

#### Scenario: Opening a file outside all roots
- **GIVEN** roots `/data/books` only
- **WHEN** the user tries to open `/home/u/Downloads/book.m4b`
- **THEN** the system refuses, explains that the file is outside every library root, and points to adding a root in settings
