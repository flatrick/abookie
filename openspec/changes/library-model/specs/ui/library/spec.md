# Spec Delta

## Purpose

The parts of the library that the user sees. With them, the user sets up and manages roots, examines and corrects warnings, accepts matches, and selects a book to resume.

## ADDED Requirements

### Requirement: Root setup with preview
When the user adds a root, on the first start or later, the UI MUST show the recommended leaf mode and name pattern. It MUST show how many books agree with the tags, and a preview of sample books. The UI MUST save the root only after the user accepts.

#### Scenario: First start
- **GIVEN** no library database exists
- **WHEN** the application starts
- **THEN** a setup asks for a folder and shows the recommended leaf mode and name pattern with a preview. The library opens after the user accepts.

#### Scenario: User selects a different pattern
- **GIVEN** the setup preview recommends the hierarchy pattern
- **WHEN** the user selects the name pattern
- **THEN** the preview shows sample books with the name pattern before the user accepts

#### Scenario: User cancels the setup
- **WHEN** the user cancels the setup preview
- **THEN** the system keeps no root, no book and no warning

### Requirement: Root management
The UI MUST let the user add roots, change root settings, tell the system that a root is gone, and start a rescan. The settings are the path, the leaf mode and the name pattern. When the system refuses an operation, the UI MUST show the reason.

#### Scenario: System refuses a nested root
- **WHEN** the user adds a root that is in an existing root
- **THEN** the UI shows the reason, with the name of the existing root

#### Scenario: User changes the path of a root
- **WHEN** the user changes the path of a root
- **THEN** the UI shows how many known books of the root are at the new path. It changes the path only after the user accepts.

### Requirement: Moved-root recommendation
A new root can look like an unreachable root that moved. Then the UI MUST ask if the user wants to change the path of that root. The question MUST give the name of the unreachable root.

#### Scenario: User accepts the recommendation
- **GIVEN** an unreachable root `/mnt/nas/books`
- **WHEN** the user adds `/media/nas/books` and accepts the recommendation
- **THEN** the path of the existing root changes, and the system adds no new root

### Requirement: Warning log view
The UI MUST show the warnings of each root, with their path in the root and a clear explanation of the reason code. For each warning, the UI MUST let the user exclude the path or open its location in the file manager of the system.

#### Scenario: User excludes a path from the warning log
- **GIVEN** a warning for `Extras/`
- **WHEN** the user selects "Exclude" on the warning
- **THEN** the system adds `Extras/` to the exclusions of the root and scans the root again

#### Scenario: Library shows the number of warnings
- **GIVEN** a root has warnings
- **WHEN** the library shows
- **THEN** an indicator shows the number of warnings, and the indicator opens the warning log

### Requirement: Book list with the last played book first
The UI MUST show the books of the library with the last played book first. Each book shows its title, author, cover and progress. When the user selects an available book, the UI MUST send a play request with its saved position and speed.

#### Scenario: User resumes a book from the list
- **GIVEN** a book saved at 1h05m at 1.5x speed
- **WHEN** the user selects it in the book list
- **THEN** the UI sends a play request with the position 1h05m and the speed 1.5x

#### Scenario: Unavailable and missing books
- **WHEN** a book is unavailable (its root is unreachable) or missing (the last scan did not find it)
- **THEN** the UI shows the book differently from other books, with its status and its progress, and the user cannot play it

### Requirement: Books with a conflict
For a book with a conflict between listening states, the UI MUST show the number of saved positions, not one progress value. The UI MUST sort the book by its most recent last played time.

#### Scenario: List shows a conflict
- **GIVEN** a book with two states in conflict
- **WHEN** the book list shows
- **THEN** the book shows "2 positions", not a progress bar

### Requirement: User selects a state before playback
When the user selects a book with a conflict between states, the UI MUST ask the user to select one state. It sends no play request before this. For each state, the UI shows the position, speed and last played time.

#### Scenario: User selects a state at play
- **GIVEN** a book with the states 4h12m at 1.0x and 20m at 1.5x
- **WHEN** the user selects the book and selects 20m at 1.5x
- **THEN** the state of the book becomes 20m at 1.5x. The UI sends a play request with the position 20m and the speed 1.5x.

#### Scenario: User cancels the selection
- **WHEN** the user cancels the selection
- **THEN** the UI sends no play request, and the system keeps both states

### Requirement: Tag-match confirmation dialog
For each identity match of only the tags, the UI MUST ask the user to accept. It MUST show the paths, durations and saved positions of the two books, and let the user link the books or keep them different.

#### Scenario: UI asks for confirmation after a scan
- **WHEN** a scan finds a match of only the tags
- **THEN** the UI asks the user to accept or refuse the match, and the system links nothing until the user answers

### Requirement: Storage failure screen
When the system cannot use the stored library data, the UI MUST show the location of the data and the reason. The UI MUST let the user only stop the application or start a new library.

#### Scenario: Database that the system cannot read at the start
- **GIVEN** a library database that the system cannot read
- **WHEN** the application starts
- **THEN** a screen gives the name of the file and the problem, and shows "Quit" and "Start a new library"
