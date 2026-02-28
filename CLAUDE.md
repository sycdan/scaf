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
pytest                        # Run all tests (includes example/ domain tests)
pytest test/unit/             # Run unit tests only
pytest test/integration/      # Run integration tests only
pytest example/               # Run co-located domain action tests only
pytest -k "test_name"         # Run a single test
pytest -m "not integration"   # Skip integration tests

ruff check                    # Lint
ruff format                   # Format
ruff format --check           # Check formatting without modifying

python -m scaf call <path>    # Run a domain action
scaf serve .                  # Start local dev API server (browser UI at http://localhost:54545)
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
- `scaf/user/` — User-facing commands: `init/`, `call/`, `discover/`, `serve/`
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

Tests live in `test/unit/` and `test/integration/`. Integration tests use a sandbox fixture (temp directory). Regression tests for bugs go in `test/integration/bug/` with timestamp-based names. The `example/` directory contains test domain actions used by integration tests — these are also collected directly by `pytest` (see `pyproject.toml`: `testpaths` includes `example/`).

### `scaf serve` and Co-located Tests

`scaf serve <deck>` starts a lightweight HTTP dev server (default port 54545) with a browser UI for running domain action tests interactively. It is implemented in `scaf/user/serve/`.

Action packages can have co-located tests following this convention:

```
<action>/
  handler.py
  command.py / query.py
  conftest.py       ← pytest_generate_tests: parametrizes payload from fixture files
  test_fixtures.py  ← test functions accepting `payload` fixture
  fixtures/
    <name>.json     ← named payload fixtures (2-space indent, uuid5 hex filename if auto-saved)
```

**Fixture format:**
```json
{
  "payload": { "field": "value" },
  "description": "human-readable scenario label",
  "expectations": {
    "test_foo": true,
    "test_bar": false
  }
}
```

`expectations` maps test name → boolean. `false` causes conftest to apply `pytest.mark.xfail(strict=True)` when running under normal `pytest` (CI). This mark is **suppressed** when `SCAF_NO_XFAIL=1` is set (the server sets this during in-process runs so it measures raw outcomes).

**conftest pattern** — always use `pytest_generate_tests`, NOT `@pytest.fixture(params=...)` (the latter evaluates at import time, which breaks in-process pytest runs and re-runs):

```python
import json, os
from pathlib import Path
import pytest

def pytest_generate_tests(metafunc):
    if "payload" not in metafunc.fixturenames:
        return
    d = Path(metafunc.definition.fspath).parent / "fixtures"
    if name := os.environ.get("SCAF_FIXTURE"):
        files = [d / name] if (d / name).exists() else []
    elif d.exists():
        files = sorted(d.glob("*.json"))
    else:
        files = []
    if not files:
        return
    params = []
    for f in files:
        data = json.loads(Path(f).read_text())
        test_name = metafunc.function.__name__
        expected = data.get("expectations", {}).get(test_name, True)
        marks = (
            [pytest.mark.xfail(strict=True, reason=f"fixture expects {test_name} to fail")]
            if expected is False and not os.environ.get("SCAF_NO_XFAIL")
            else []
        )
        params.append(pytest.param(data["payload"], marks=marks, id=Path(f).stem))
    metafunc.parametrize("payload", params)
```

**Server endpoints:**
- `GET /` — browser UI (inline HTML, zero external deps)
- `GET /actions` — list of all action paths in the deck
- `GET /actions/<path>/tests` — list of test node IDs (AST-parsed from `test_fixtures.py`)
- `POST /actions/<path>/run` — saves fixture, runs selected tests in-process, returns `{"results": [...]}`

The server runs pytest in-process (`pytest.main()`) with `--import-mode=importlib`, `--override-ini` flags to avoid picking up the project's `pyproject.toml` config, and `-p no:capture` to avoid a Windows crash where nested in-process pytest calls fail with `ValueError: I/O operation on closed file` (pytest's `_windowsconsoleio_workaround` in `capture.py` corrupts `sys.stdin` on the outer run). `import pytest` is lazy (inside the handler) so `scaf serve` works even without pytest installed.

**Subprocess tests must use `sys.executable, "-m", "scaf"` instead of just `"scaf"`** to avoid resolving to a system-installed version of scaf (e.g. older version at `%APPDATA%/Python/Scripts/scaf`) rather than the current dev editable install.

`dev/test/handler.py` (used by the pre-push hook) runs pytest in-process with `--import-mode=importlib` and correctly returns `success = result == 0` based on pytest's exit code.

Fixture filenames are deterministic: `uuid.uuid5(uuid.NAMESPACE_DNS, canonical_json).hex + ".json"` where `canonical_json = json.dumps(payload, separators=(",",":"), sort_keys=True)`.

## Code Style

- 2-space indentation, 99-character line length (enforced by ruff)
- Action input shapes are plain `@dataclass` classes — no ORM, no pydantic
- `handle()` in `handler.py` is always the action entrypoint
- Handlers may print to stderr (e.g. progress, warnings) but never to stdout — stdout is reserved for the JSON result emitted by `scaf/output.py`

## Key Constraint

If user-facing functionality is broken, fix it before refactoring or adding features.
