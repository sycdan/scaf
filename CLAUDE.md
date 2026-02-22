# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Self-Maintenance

**Each session:** verify this file still accurately describes the codebase before starting work. Update it whenever you discover outdated, missing, or incorrect information during a session. Keeping this file accurate is high-priority — stale guidance causes mistakes.

## What This Is

Scaf is a filesystem-based project builder and domain-action runner for Python. It lets users define domain actions as Python modules in a folder hierarchy and invoke them via CLI. Zero external dependencies in the core package (dev deps: pytest, pytest-cov, ruff, vulture).

Requires Python 3.14+. Only bash is supported as a shell.

## Development Setup

```bash
source dev/env.sh        # Create venv, install deps (editable), install git hooks
source dev/env.sh --nuke # Nuke and recreate environment (required after package/hook changes)
```

## Commands

```bash
pytest                        # Run all tests
pytest test/unit/             # Run unit tests only
pytest test/integration/      # Run integration tests only
pytest -k "test_name"         # Run a single test
pytest -m "not integration"   # Skip integration tests

ruff check                    # Lint
ruff format                   # Format
ruff format --check           # Check formatting without modifying

python -m scaf call <path>    # Run a domain action
```

The pre-push hook enforces: clean working tree, formatted/linted code (`ruff check && ruff format --check`), and passing tests (`pytest`).

## Architecture

### Domain-Driven Design

Scaf projects organize code as a filesystem hierarchy of domains, capabilities, entities, and actions.

```
<domain>/<capability>/<action>/
    command.py   # Dataclass defining input shape (for write actions)
    query.py     # Dataclass defining input shape (for read-only actions)
    handler.py   # Contains handle() function — the execution logic

<domain>/<capability>/<entity>/
    entity.py    # Dataclass defining entity shape
    rules.py     # Validation/fitting logic
```

Key naming conventions:
- Domains and capabilities: singular nouns (e.g., `skynet/defense/`, not `defenses/`)
- Actions: verbs or verb-noun (e.g., `fire_nukes/`, `get/`, `deploy/`)
- The last path segment before an action is the **capability**; everything before is the **domain**
- Capable entities (with their own actions) nest actions inside the entity folder

### Scaf's Own Code (`scaf/`)

The scaf package itself follows the same domain-action pattern:

- `scaf/cli.py` — Entry point; routes `scaf init`, `scaf call`, `scaf version`
- `scaf/user/` — User-facing commands: `init/`, `call/`, `discover/`
- `scaf/action_package/` — Core machinery:
  - `load/` — Dynamically imports `command.py`/`query.py` + `handler.py` from a filesystem path
  - `invoke/` — Parses CLI args from dataclass fields and calls `handle()`
  - `create/` — Auto-creates missing action folder skeletons
- `scaf/deck/` — Deck (project root) management; `locate/` finds the `.scaf/` folder up the tree
- `scaf/alias/` — Generates bash alias file (`.scaf/aliases`) for quick action invocation
- `scaf/tools.py` — Naming utilities (snake/camel/slug conversion), dynamic module loading
- `scaf/rules.py` — Field validation via "fitter" functions
- `scaf/output.py` — Custom JSON encoder (handles dataclasses, Path, UUID, datetime); all action results go to stdout as JSON
- `scaf/config/` — Constants, logging config (SCAF_VERBOSITY env var: 0=ERROR…3=DEBUG)

### Execution Flow

1. `scaf call example/domain/action [args...]`
2. CLI routes to `user/call/handler.py`
3. Deck is located (`.scaf/` folder search up directory tree)
4. `action_package/load/` dynamically imports the action module
5. `action_package/invoke/` parses CLI args from the dataclass fields
6. `handler.handle()` executes and returns a result
7. `output.py` serializes result to JSON on stdout

### Testing

All features must be built with TDD: write the integration test first (confirm it fails), then implement until it passes.

Tests live in `test/unit/` and `test/integration/`. Integration tests use a sandbox fixture (temp directory). Regression tests for bugs go in `test/integration/bug/` with timestamp-based names. The `example/` directory contains test domain actions used by integration tests.

## Code Style

- 2-space indentation, 99-character line length (enforced by ruff)
- Action input shapes are plain `@dataclass` classes — no ORM, no pydantic
- `handle()` in `handler.py` is always the action entrypoint
- Handlers may print to stderr (e.g. progress, warnings) but never to stdout — stdout is reserved for the JSON result emitted by `scaf/output.py`

## Key Constraint

If user-facing functionality is broken, fix it before refactoring or adding features.
