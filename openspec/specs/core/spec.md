# core Specification

## Purpose
Cross-cutting rules for every capability under `core/`: core holds the application's behavior as pure logic, isolated from UI, playback engine, storage technology and operating system.

## Requirements

### Requirement: Core is independent of UI, engine and OS libraries
Core SHALL NOT depend on any UI toolkit, playback engine, tag-reading library, storage engine or OS-specific facility; it interacts with them only through ports it defines.

#### Scenario: Layering check on the core package
- **WHEN** the automated layering check runs as part of the test suite
- **THEN** it fails if any core module imports a UI, engine, tag, storage or OS-integration library, or any module from the ui or platform layers

#### Scenario: Core runs without native dependencies
- **GIVEN** an environment where the playback engine library and display server are unavailable
- **WHEN** the core test suite runs
- **THEN** every core test executes and passes

### Requirement: All external effects go through ports
Core SHALL perform every effect outside pure computation (playback, filesystem access, tag reading, persistence, OS notifications) through a port interface, and every port SHALL have a test double usable in core tests.

#### Scenario: Port has a test double
- **WHEN** a new port is added to core
- **THEN** a test double implementing that port exists in the test suite and at least one core test uses it

### Requirement: Time comes from an injected clock
Core SHALL obtain the current time and schedule delayed work only through an injected clock port, never from the system clock directly.

#### Scenario: Time-dependent behavior is tested without waiting
- **GIVEN** core behavior that depends on elapsed time (for example a periodic position save)
- **WHEN** its test advances a fake clock
- **THEN** the behavior triggers without the test sleeping in real time
