# Spec Delta

## Purpose

Defines how the system finds the start and the end of each book in a library root, at all folder depths. It also defines how the system fills metadata from the path when the tags do not give it.

## ADDED Requirements

### Requirement: Each root has a leaf mode and a name pattern
Each library root MUST have one leaf mode (`folder` or `file`) and one name pattern. The user accepts both when the user adds the root, and the user can change them later.

#### Scenario: User changes the leaf mode of a root
- **GIVEN** a root with the leaf mode `folder`
- **WHEN** the user changes it to `file`
- **THEN** the system keeps the new leaf mode and scans the root again

### Requirement: Folders with audio are books
In leaf mode `folder`, the system MUST make one book from each folder that contains audio files and that has no subfolder with audio. The depth of the folder in the root is not important.

#### Scenario: Books at different depths
- **GIVEN** a root in leaf mode `folder`
- **WHEN** it contains `Author A/Book B/01.mp3` and `Author A/Series S/Book C/01.mp3`
- **THEN** `Author A/Book B` and `Author A/Series S/Book C` are both books

#### Scenario: Book folder with an image subfolder
- **GIVEN** a root in leaf mode `folder`
- **WHEN** it contains `Author A/Book B/01.mp3` and `Author A/Book B/scans/page1.jpg`
- **THEN** `Author A/Book B` is a book, and the system writes no warning

#### Scenario: Book with many files in an author folder
- **GIVEN** a root in leaf mode `folder`
- **WHEN** it contains `Author A/part-001.m4b` to `Author A/part-125.m4b`, and `Author A` has no subfolders
- **THEN** `Author A` is one book with 125 files

### Requirement: Folders that contain only folders are groups
In leaf mode `folder`, the system MUST use a folder with no audio files as a group, and MUST look for books in its subfolders. This is not true when all subfolders are disc folders.

#### Scenario: Anthology folder
- **GIVEN** a root in leaf mode `folder`
- **WHEN** it contains `Series S/Anthology/01 Story/a.mp3` and `Series S/Anthology/02 Story/a.mp3`
- **THEN** `Series S/Anthology/01 Story` and `Series S/Anthology/02 Story` are two different books

### Requirement: System ignores folders without audio
The system MUST ignore a folder that contains no audio files at any depth. It makes no book and writes no warning for that folder.

#### Scenario: Folder with only ebook files
- **GIVEN** a folder that contains only `book.epub`, `metadata.opf` and `cover.jpg`
- **WHEN** the system scans its root
- **THEN** the system makes no book and writes no warning for the folder

### Requirement: Tracks are in natural order
The system MUST put the audio files of a book with many files in the natural sort order of their names.

#### Scenario: Natural sort of tracks
- **GIVEN** a book folder that contains `1.mp3`, `2.mp3` and `10.mp3`
- **WHEN** the system finds the track order of the book
- **THEN** the order is `1.mp3`, `2.mp3`, `10.mp3`

### Requirement: Disc folders are one book
The system MUST make one book from a folder that has no audio files and whose subfolders all have a disc name and contain audio. A disc name is CD, Disc or Part, followed by a number. The discs play in natural order.

#### Scenario: Book in disc folders
- **GIVEN** a folder that contains only `CD1/` and `CD2/`, and each disc folder contains audio files
- **WHEN** the system finds the track order of the book
- **THEN** the folder is one book, and all tracks of `CD1` come before all tracks of `CD2`. The tracks of each disc are in natural order.

### Requirement: File leaf mode
In leaf mode `file`, the system MUST make one book from each audio file in the root, at all depths.

#### Scenario: Single-file books in one folder
- **GIVEN** a root in leaf mode `file`
- **WHEN** it contains `Author A/Book One.m4b` and `Author A/Book Two.m4b`
- **THEN** the system makes two books, one for each file

### Requirement: System finds audio by extension
The system MUST find audio files by their extension, in upper case or lower case. The extensions are `m4b m4a mp3 opus ogg flac wav aac wma`.

#### Scenario: Upper case and different formats
- **GIVEN** a book folder that contains `01.MP3`, `02.wma` and `03.mp3`
- **WHEN** the system scans the root
- **THEN** all three files are tracks of the book

### Requirement: System ignores files that are not audio
The system MUST ignore files in book folders that are not audio, and MUST NOT write warnings for them. The system MUST use an image file with the name `cover` or `folder` as the cover of the book.

#### Scenario: Cover image and metadata files
- **GIVEN** a book folder that contains `01.mp3`, `cover.jpg` and `info.nfo`
- **WHEN** the system scans the root
- **THEN** the system makes one book with `cover.jpg` as its cover, and writes no warnings

### Requirement: Book metadata comes from tags first
The system MUST use the `album` tag as the title of a book. It MUST use the first tag that has a value as the author, in the sequence `albumartist`, `artist`, `composer`. A tag that is empty or that contains only spaces has no value.

#### Scenario: Title from album
- **GIVEN** a book with tracks that have the `album` "Mort" and the `title` "Chapter 1"
- **WHEN** the system reads the metadata of the book
- **THEN** the title of the book is "Mort"

#### Scenario: Empty albumartist
- **GIVEN** a book with an empty `albumartist` tag and the `artist` tag "Jane Doe"
- **WHEN** the system reads the metadata of the book
- **THEN** the author is "Jane Doe"

### Requirement: Name patterns fill metadata that the tags do not give
The system MUST use the name pattern of the root only to fill a title or an author that the tags do not give. For each value, the system MUST record if it came from the tags or from the path.

#### Scenario: No author tag, with the hierarchy pattern
- **GIVEN** a root with the hierarchy pattern, and a book at `Jane Doe/Series S/Some Book` with no author tags
- **WHEN** the system reads the metadata of the book
- **THEN** the author is "Jane Doe", and its source is the path

#### Scenario: No tags, with the name pattern
- **GIVEN** a root with the name pattern, and a book folder `Jane Doe - Some Book` with no tags
- **WHEN** the system reads the metadata of the book
- **THEN** the author is "Jane Doe" and the title is "Some Book", and the source of both is the path

### Requirement: Built-in name patterns
The system MUST supply two name patterns. The hierarchy pattern uses the first folder in the root as the author, and the name of the book as the title. The name pattern divides the name of the book at the first ` - `.

#### Scenario: Hierarchy pattern for a book in the root folder
- **GIVEN** a root with the hierarchy pattern, and a book with no tags at `Some Book`
- **WHEN** the system reads the metadata of the book
- **THEN** the title is "Some Book", and the system does not fill the author from the path

#### Scenario: System keeps the pattern as text
- **WHEN** the system saves a root with the name pattern
- **THEN** the pattern of the root is the text `{author} - {title}`

### Requirement: Book name is the title when the pattern does not agree
When the name pattern does not agree with the path of a book, the system MUST use the folder name as the title. In leaf mode `file`, it uses the file name without the extension. The system fills no other field from the path and writes no warning.

#### Scenario: Name without a dash
- **GIVEN** a root with the name pattern, and a book folder `Some Book` with no tags
- **WHEN** the system reads the metadata of the book
- **THEN** the title is "Some Book", the system fills no author, and the system writes no warning

### Requirement: Setup recommends a leaf mode and name pattern
When the user adds a root or edits its settings, the system MUST compare the leaf modes and name patterns with sample tags. The system MUST recommend the best result and show a preview of sample books.

#### Scenario: Recommendation from tags
- **GIVEN** a folder in which most books with tags have an author tag that is the same as their first folder name
- **WHEN** the user adds the folder as a root
- **THEN** the system recommends the hierarchy pattern, shows how many books agree, and shows a preview of sample books

#### Scenario: No tags for the comparison
- **GIVEN** a folder in which the sample books have no author tags and no album tags
- **WHEN** the user adds the folder as a root
- **THEN** the system recommends no pattern, and the user selects a pattern from the preview

#### Scenario: Different albums in each book folder
- **GIVEN** a folder in which each book folder contains files with different album tags
- **WHEN** the user adds the folder as a root
- **THEN** the system recommends the leaf mode `file`
