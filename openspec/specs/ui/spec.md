# ui Specification

## Purpose
Cross-cutting rules for every capability under `ui/`: the UI presents core behavior and forwards user intent, but holds no business logic of its own.

## Requirements

### Requirement: Views hold no business logic
UI views SHALL only render state and forward user actions; every decision about application behavior SHALL live in core or in a view-model backed by core.

#### Scenario: Behavior is testable without rendering
- **WHEN** a user-facing behavior is added (for example "resume a book at its saved position")
- **THEN** it is covered by tests of core or of a view-model that run without displaying any window

### Requirement: UI reaches core only through view-models
UI views SHALL NOT call platform adapters directly; they SHALL interact with application behavior only through view-models.

#### Scenario: Layering check on the ui package
- **WHEN** the automated layering check runs as part of the test suite
- **THEN** it fails if any view module imports a platform-layer module
