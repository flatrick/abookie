# Spec Delta

## Purpose

Defines how the system finds that a book is the same book after a scan, a move to a different root, or a relocation. Thus the listening state stays with the book when its files move or get a new name. It also defines how the system merges two known books.

## ADDED Requirements

### Requirement: Books have identity claims
Each book MUST have a set of identity claims. Each claim has a kind and a value. It MUST be possible to add new claim kinds without a change to the existing claims.

#### Scenario: System records claims for a new book
- **GIVEN** a root with the path `/data/books`, and a new book at `Author A/Book B` in it
- **WHEN** the system finds the book for the first time
- **THEN** the book has an `abs_path` claim `/data/books/Author A/Book B` and a `rel_path` claim `Author A/Book B`. It also has a `tags` claim if it has an author tag and a title tag.

#### Scenario: Claim of an unknown kind
- **GIVEN** a claim of a kind that the current version does not use
- **WHEN** the system compares identities
- **THEN** the system keeps the claim without a change and does not use it in the comparison

### Requirement: MVP claim kinds
In the MVP, the system MUST make and compare only the claim kinds `abs_path`, `rel_path` and `tags`.

- `abs_path` is the root path and the path of the book in the root together.
- `rel_path` is the path of the book in the root.
- `tags` is the author and the title in a standard form.

#### Scenario: Book without author or title tags
- **WHEN** the system finds a book with no author tag or no album tag
- **THEN** the book gets an `abs_path` claim and a `rel_path` claim, and no `tags` claim

### Requirement: System compares claims in a fixed sequence
When a scan finds a book, the system MUST compare it with the known books in this sequence: `abs_path`, `rel_path`, `tags`. The first kind that agrees MUST give the result.

#### Scenario: Same location
- **WHEN** a scan finds a book with an absolute path that is the same as the `abs_path` claim of a known book
- **THEN** it is the same book

### Requirement: A rel_path match in the same root is always correct
When a found book has the same `rel_path` as a known book in the same root, the system MUST link the two books. It changes the `abs_path` claim. It does no other checks.

#### Scenario: User changes the root path
- **GIVEN** a known book with the claim `rel_path` = `Author A/Book B`, in a root whose path changed from `/mnt/nas/books` to `/media/nas/books`
- **WHEN** the rescan finds `Author A/Book B`
- **THEN** it is the same book, and its `abs_path` claim changes to `/media/nas/books/Author A/Book B`

### Requirement: Links between roots need the old location to be gone
When a claim agrees with a known book in a different root, the system MUST link the books only if the old location is gone. This applies to `rel_path` and `tags` claims.

The old location is gone in two conditions. The first is when the user said that its root is gone. The second is when its root is reachable and the old path does not exist.

#### Scenario: User moves a book to a different reachable root
- **GIVEN** a known book with the `rel_path` `Author A/Book B` in the reachable root 1, and its folder does not exist
- **WHEN** a scan of root 2 finds `Author A/Book B`
- **THEN** it is the same book, and the system changes its path claims

#### Scenario: Two copies exist
- **GIVEN** a known book at `/data/a/Author A/Book B` that exists
- **WHEN** a scan of a different root finds `Author A/Book B`
- **THEN** the found book is a new and different book

#### Scenario: Old root offline
- **GIVEN** a known book `Author A/Book B` in a root that is unreachable, and the user did not say that the root is gone
- **WHEN** a scan of a different root finds `Author A/Book B`
- **THEN** the found book is a new and different book, and the known book stays unavailable

### Requirement: Tag matches need the agreement of the user
The system MUST NOT link or merge two books automatically when only the `tags` claim agrees. The system MUST ask the user, and MUST show the paths, total durations and saved positions of the two books.

#### Scenario: User accepts a tag match
- **GIVEN** a known book with the `tags` claim author "Jane Doe" and title "Some Book", and its old location is gone
- **WHEN** a scan finds a folder with a new name and the same tags, and the user accepts
- **THEN** the system links the found book to the known book, and the book keeps its listening state

#### Scenario: User refuses a tag match
- **WHEN** the user does not accept a tag match
- **THEN** the found book stays a different book, and the known book does not change

### Requirement: Merge of two known books
When the system links two books that it knows already, it MUST merge them into one book that has the claims of the two books. It MUST keep the listening state of the two books as the listening-state conflict rules tell.

#### Scenario: User accepts a tag match for a book that the user played
- **GIVEN** a tag match between the known book A and the found book B that waits for the user, and the user played B
- **WHEN** the user accepts the match
- **THEN** A and B become one book with the claims of the two books. The system keeps the two listening states as a conflict.

### Requirement: A root that is gone causes merges by rel_path
When the user says that a root is gone, the system MUST merge each of its books with a book that has the same `rel_path`. It does this automatically. The system MUST ask the user about matches of only the `tags` claim.

#### Scenario: Copy of the book in a different root
- **GIVEN** the book A `Author A/Book B` in an unreachable root, and the book B with the same `rel_path` in a different root. The system made book B when the first root was offline.
- **WHEN** the user says that the unreachable root is gone
- **THEN** the system merges A and B into one book, and does not ask the user

### Requirement: System keeps missing books
The system MUST keep a known book that no scan finds, and MUST show it as missing with its listening state. The system MUST NOT delete it automatically.

#### Scenario: User deletes a book from the disk
- **GIVEN** a known book with a saved position in a reachable root
- **WHEN** its files are deleted and the system scans its root again
- **THEN** the system shows the book as missing with its saved position, until the user removes it
