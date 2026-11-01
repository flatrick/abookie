# Contributing to abookie

## Test-driven development is mandatory

Every change follows Red-Green-Refactor:

1. **Red**: write a test that fails because the behavior does not exist yet. Run it and watch it fail.
2. **Green**: write the minimal code that makes it pass.
3. **Refactor**: clean up with all tests green.

Do not write implementation code without a failing test that requires it. The test suite enforces the layering rules (`core` / `platform` / `ui`) and a coverage floor of 80%.

## Planning changes

Changes are planned with [OpenSpec](https://github.com/Fission-AI/OpenSpec) under `openspec/changes/`. A change's proposal, design, specs and tasks are committed before any code for it. See [AGENTS.md](AGENTS.md) for the workflow.

## Commits

Commit messages follow Conventional Commits and are checked by gir. See [GIT-IT-RIGHT.md](GIT-IT-RIGHT.md).

## Dependencies

Declare dependencies in `pyproject.toml`. Never copy (vendor) third-party code into the repository. GPL and LGPL dependencies are acceptable.

## Public-domain dedication

abookie is released under [The Unlicense](LICENSE). By submitting a contribution, you dedicate it to the public domain under the same terms. Include this statement in your first pull request:

> I dedicate any and all copyright interest in this software to the public domain. I make this dedication for the benefit of the public at large and to the detriment of my heirs and successors. I intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.
