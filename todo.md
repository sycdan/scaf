# Scaf Development Roadmap

**Note:** Always use TDD (write a failing test, then make it pass).

## [ ] Dev API for tests

We want to enable `scaf serve ./deck/path` (exposed as a userspace action, like discover)

It should start a lightweight API to serve as ingress to the domain action and their tests.

There will be a form with an input box that can take arbitrary json and an optional description (e.g. "failed request from bug reported on `yyyymmdd`"), and you can click on one of the actions paths exposed in the served alias file to select that action as the target for the payload, and then select one or more tests defined in that action package, providing an expected outcome for each (pass/fail) and an optional reason. On submit, the controller will:

- load the target action package
- hash the payload (e.g. non-indented json dumps with sort keys)
- save it as a fixture in the action folder/fixtures dir (2-space indent, not sorted)
- run the payload fixture through selected test(s), somehow executing it with only that fixture and not the full list of possibilities

For example if a user reports an error with a domain action, we can log the payload then a dev can run it through the integration tests and debug.

e.g. we might have a test_validation integration test, and you can give it a payload you expect to be good or bad, and see if the domain agrees -- if the test fails, then you have a paramterized fixture added to the codebase for TDD purposes and then future regression testing.

We need to be able to run the server with debugpy in a way that we don't need to manually restart the server if modify the domain action code.

We will not seek to integrate the existing ./test domain into this paradigm -- only add new tests this way (we can gradually convert older tests).

---

### Phase 1 — `serve` userspace action skeleton

- [x] Add `scaf/user/serve/command.py` (`Serve` dataclass: `deck: Deck`, `port: int = 54545`)
- [x] Add `scaf/user/serve/handler.py` (stub: start server, block on serve loop)
- [x] Integration test: `scaf serve --help` exits 0 and includes `port` in output if easy

### Co-located test convention (new, not for existing tests)

Each action package that wants serve-compatible tests follows this layout:

```
<action>/
  handler.py
  command.py / query.py
  conftest.py          ← provides `payload` fixture via pytest_generate_tests
  test_fixtures.py     ← tests that accept `payload` as a parameter
  fixtures/
    <descriptive_name>.json   ← named payloads (2-space indent, keys unsorted)
```

Fixture format:
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

`conftest.py` pattern (use `pytest_generate_tests`, NOT `@pytest.fixture(params=...)` — avoids import-time evaluation which breaks in-process pytest runs):
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
            if expected is False
            else []
        )
        params.append(pytest.param(data["payload"], marks=marks, id=Path(f).stem))
    metafunc.parametrize("payload", params)
```

- [x] Tests use `payload` like any other pytest fixture — no sandbox, no subprocess, real code
- [x] `pyproject.toml` includes `example/` in `testpaths` — domain tests run under normal `pytest`
- [x] Fixture `"expectations"` dict maps test name → `"pass"|"fail"`; conftest applies `xfail(strict=True)` for TDD/regression tracking
- [x] Example domain action tests: `example/hole/insert_peg/test_fixtures.py` + fixtures

### Phase 2 — HTTP server + action discovery endpoints

- [x] `GET /actions` — calls `find_available_actions` on the deck, returns JSON list of action paths
- [x] `GET /actions/<path>/tests` — runs `pytest --collect-only -q <action_path>`, parses output to list `test_*` node IDs; returns JSON list
- [x] Integration tests for both endpoints (spin up server in a thread, hit with `urllib`)

### Phase 3 — Payload POST, fixture save, test execution

On `POST /actions/<path>/run` with body `{"payload": {...}, "description": "...", "tests": [{"name": "...", "expect": "pass"|"fail"}]}`:

1. Hash payload: `sha256(json.dumps(payload, separators=(',',':'), sort_keys=True))`
2. Write fixture to `<action>/fixtures/<hash>.json` (2-space indent, keys unsorted)
3. For each selected test: run `SCAF_FIXTURE=<hash>.json pytest <action>/test_foo.py::<test_name>`
4. Return `{"results": [{"test": "...", "expected": "...", "actual": "...", "passed": bool}]}`
- [x] Integration test: POST triggers fixture write and correct pass/fail result

### Phase 4 — Frontend UI (single inline HTML, zero external deps)

Served from `GET /`:

- [x] JSON textarea (payload input)
- [x] Optional description field
- [x] Action selector dropdown (populated from `GET /actions`)
- [x] Test checkboxes (populated from `GET /actions/<path>/tests` on action change)
- [x] Per-test expected outcome toggle (pass / fail)
- [x] Submit → `POST /actions/<path>/run` → render results table inline

### Phase 5 — Hot reload

- [x] File watcher: poll `os.stat` on the deck path; `exec` affected module's source code into the existing module object in `sys.modules` on change (note: `importlib.reload` uses cached bytecode so won't work; `exec(compile(source, ...), mod.__dict__)` is used instead)
- [x] Integration test: `FileWatcher` detects change and updates module in `sys.modules` directly

---

**TDD order:** Write each failing integration test first, then implement until it passes.
