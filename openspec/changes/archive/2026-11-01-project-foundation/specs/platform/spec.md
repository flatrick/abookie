# Spec Delta

## Purpose

Cross-cutting rules for every capability under `platform/`: adapters connect core ports to real engines, storage and operating systems, and are the only place OS-specific code may live.

## ADDED Requirements

### Requirement: Adapters implement core ports
Every platform adapter SHALL implement a port defined by core and SHALL be verified by an integration test against the real dependency it wraps.

#### Scenario: Adapter integration test
- **WHEN** the integration test suite runs on a machine with the adapter's system dependency installed
- **THEN** each adapter is exercised against the real dependency using committed test fixtures

### Requirement: OS-specific code lives only in platform
Code that only works on a specific operating system SHALL reside in the platform layer; core and ui SHALL contain no OS-conditional behavior.

#### Scenario: Adding a new operating system
- **WHEN** support for a new operating system is added
- **THEN** the required changes are confined to the platform layer plus application wiring, with no changes to core behavior

### Requirement: Missing system dependencies are reported clearly
The application SHALL detect a missing required system dependency at startup and SHALL report which dependency is missing and how to install it, instead of failing with an unhandled error.

#### Scenario: Playback engine library not installed
- **GIVEN** the playback engine's system library is not installed
- **WHEN** the user starts the application
- **THEN** the application shows a message naming the missing library and how to install it, and exits without a traceback
