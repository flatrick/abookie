# Spec Delta

## Purpose

The user-facing parts of the library: setting up and managing roots, reviewing and resolving warnings, and picking a book to resume.

## ADDED Requirements

### Requirement: First-run root setup
On first run the UI SHALL guide the user to pick a root folder and its structure before showing the library, suggesting the user's audiobook or music folder when one exists.

#### Scenario: First launch
- **GIVEN** no roots are configured
- **WHEN** the application starts
- **THEN** a setup flow asks for a folder and a structure preset, and the library opens after both are chosen

### Requirement: Root management
The UI SHALL let the user add roots, remove roots, change a root's structure and trigger a rescan, and SHALL show the reason whenever an action is refused.

#### Scenario: Nested root refused
- **WHEN** the user adds a root nested in an existing one
- **THEN** the UI shows the refusal reason naming the existing root

### Requirement: Warning log view
The UI SHALL show each root's warnings with their relative path and a human-readable explanation of the reason code, and SHALL offer per-warning actions to exclude the path or open its location in the system file manager.

#### Scenario: Excluding from the warning log
- **GIVEN** a warning for `Extras/`
- **WHEN** the user chooses "Exclude" on it
- **THEN** `Extras/` is added to the root's exclusions and the root is rescanned

#### Scenario: Warnings are visible from the library
- **GIVEN** a root has warnings
- **WHEN** the library is shown
- **THEN** a visible indicator shows the number of warnings and opens the warning log

### Requirement: Book list ordered by last played
The UI SHALL show the library's books sorted by most recently played, each with title, author, cover and progress, and selecting a book SHALL resume it at its saved position and speed.

#### Scenario: Resume from the list
- **GIVEN** a book saved at 1h05m at 1.5x speed
- **WHEN** the user selects it in the book list
- **THEN** playback resumes at 1h05m at 1.5x

#### Scenario: Unavailable and missing books
- **WHEN** a book is unavailable (root unreachable) or missing (not found by the last scan)
- **THEN** it is shown visually distinct with its status, keeps its progress display, and cannot be played

### Requirement: Tag-match confirmation dialog
The UI SHALL present each tag-only identity match as a confirmation showing both books' paths, durations and saved positions, with explicit choices to link or to keep them separate.

#### Scenario: Confirmation shown after a scan
- **WHEN** a scan produces a tag-only match
- **THEN** the user is asked to confirm or reject it, and nothing is linked until they answer
