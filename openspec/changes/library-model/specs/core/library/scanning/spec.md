# Spec Delta

## Purpose

Defines how the system finds books in a library root. It also defines how the system tells the user about content that it cannot put into a book, and how the user corrects it.

## ADDED Requirements

### Requirement: When the system scans a root
The system MUST scan a root at these times: when the user adds it, when its settings change, and when the user starts a rescan. The settings are the path, the leaf mode and the name pattern. The system MUST NOT monitor the filesystem for changes.

#### Scenario: User adds a root
- **WHEN** the user adds a root and accepts its settings
- **THEN** the system scans the root, and its books show in the library

#### Scenario: User adds files after the last scan
- **GIVEN** a root that the system scanned
- **WHEN** the user copies a new book folder into the root and does not start a rescan
- **THEN** the library does not show the new book until the next scan

### Requirement: Scans never change the files of the user
Scans and all other library operations MUST NOT make, move, rename, change or delete a file in a library root.

#### Scenario: Scan of a root with warnings
- **GIVEN** a root that contains files that the system cannot put into books
- **WHEN** the system scans the root
- **THEN** after the scan, the content and the name of each file in the root are the same as before

### Requirement: System applies all results of a scan or none
The system MUST apply all the results of a root scan together. If a scan stops before the end, the library MUST stay as it was before the scan.

#### Scenario: Application stops during a scan
- **GIVEN** a root that the system scans again
- **WHEN** the application is killed before the scan is complete
- **THEN** at the next start, the books, warnings and listening state of the root are the same as before the scan

### Requirement: Each warning has a reason code
The system MUST write one warning in the warning log of a root for each path that it cannot put into a book. The warning MUST contain the path in the root and a reason code from a fixed set.

#### Scenario: Set of reason codes
- **WHEN** the system writes a warning
- **THEN** its reason is one of these: `mixed-files-and-folders`, `invalid-disc-layout`, `audio-in-root`, `unreadable-audio`, `multiple-albums-in-book`, `symlink-not-followed`

#### Scenario: Audio next to subfolders with audio
- **GIVEN** a root in leaf mode `folder`, and a folder `Book B` that contains `intro.mp3` and `CD1/01.mp3`
- **WHEN** the system scans the root
- **THEN** the system writes one warning with the reason `mixed-files-and-folders` and the path `Book B`, and makes no book from `Book B`

#### Scenario: Disc folders and other folders together
- **GIVEN** a root in leaf mode `folder`, and a folder `Book B` with no audio files that contains `CD1/01.mp3`, `CD2/01.mp3` and `Extras/bonus.mp3`
- **WHEN** the system scans the root
- **THEN** the system writes one warning with the reason `invalid-disc-layout` and the path `Book B`, and makes no book from `Book B` or from its subfolders

#### Scenario: Audio directly in the root
- **GIVEN** a root in leaf mode `folder`
- **WHEN** the root folder contains the file `stray.mp3`
- **THEN** the system writes a warning with the reason `audio-in-root` and the path `stray.mp3`

#### Scenario: Audio file that the system cannot read
- **GIVEN** a book folder that contains `01.mp3`, which the system cannot read as audio, and other tracks that it can read
- **WHEN** the system scans the root
- **THEN** the system writes a warning with the reason `unreadable-audio` and the path of the file. The book has only the tracks that the system can read.

#### Scenario: Two albums in one book folder
- **GIVEN** a root in leaf mode `folder`, and a book folder with files that have two different album tags
- **WHEN** the system scans the root
- **THEN** the folder is one book, and the system writes a warning with the reason `multiple-albums-in-book` and the path of the folder

### Requirement: System does not follow symbolic links
The system MUST NOT follow symbolic links in a root. The system MUST write a warning with the reason `symlink-not-followed` for each symbolic link.

#### Scenario: Book folder that is a symbolic link
- **GIVEN** a root in which `Author A/Book B` is a symbolic link to a folder in a different location
- **WHEN** the system scans the root
- **THEN** the system makes no book from `Author A/Book B`, and writes a warning with the reason `symlink-not-followed` and that path

#### Scenario: Symbolic link to a parent folder
- **GIVEN** a root that contains a symbolic link to one of its own parent folders
- **WHEN** the system scans the root
- **THEN** the scan completes, and the system writes a warning with the reason `symlink-not-followed` for the link

### Requirement: System keeps the warning log until the next scan
The system MUST keep the warning log of a root in permanent storage. The results of the next scan of that root MUST replace all of the log.

#### Scenario: Warnings stay after a new start
- **GIVEN** a root that had warnings from its last scan
- **WHEN** the application starts again
- **THEN** the application shows the same warnings

#### Scenario: Warning goes away after the user corrects it
- **GIVEN** a warning for `stray.mp3`
- **WHEN** the user moves the file into a book folder and starts a rescan
- **THEN** the warning does not show

### Requirement: User can exclude a path from a root
The user MUST be able to exclude a path in a root from the library of that root. Scans skip the excluded path and all content in it, and make no books and no warnings from it.

#### Scenario: User excludes a path that has a warning
- **GIVEN** a warning for `Extras/` in a root
- **WHEN** the user excludes `Extras/` and starts a rescan
- **THEN** the system makes no books and no warnings from `Extras/` or from its content

#### Scenario: Exclusion for a path that does not exist
- **GIVEN** an exclusion for `Extras/` in a reachable root
- **WHEN** a rescan finds that `Extras/` does not exist
- **THEN** the system removes the exclusion and tells the user
