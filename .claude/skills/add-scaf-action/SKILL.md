---
name: add-scaf-action
description: Implement a new scaf domain action (query or command) as an action package. Use when asked to add/implement a `scaf call <path>` action, a scaf query, a scaf command, or a new user-facing scaf subcommand. Covers the file layout, the Shape dataclass pattern, deck/alias helpers, and the TDD workflow this repo requires.
---

# Add a scaf action

A scaf action is an **action package**: a folder whose last segment is a verb (or verb_noun).
The CLI discovers it by path — no registration needed.

## Required files

`must_contain_required_files` (`scaf/action_package/rules.py`) enforces:

- `__init__.py` (empty)
- `handler.py` — contains `handle()`
- `command.py` **OR** `query.py` — the input Shape dataclass

Use `query.py` for read-only actions, `command.py` for write actions. The distinction is convention; both are loaded identically.

## The Shape (query.py / command.py)

```python
from dataclasses import dataclass

from scaf.core import Shape


@dataclass
class Show(Shape):  # class name = CamelCase of the action folder
  """One-line docstring — shown as the action's description in `scaf show` / help."""

  # Fields become CLI args (see "Fields → CLI" below). Omit fields for a no-arg action.

  def execute(self):
    from scaf.user.show.handler import handle  # lazy import avoids import cycles

    return handle(self)
```

- Inherit from `Shape` (`from scaf.core import Shape`). It runs `values_must_fit()` on init and calls optional `prepare()`.
- The **first dataclass** in the module is picked up (`extract_first_dataclass`); names starting with `_` are skipped.
- A `Result` nested dataclass is optional — return it from `handle()` and `output.py` serializes it to JSON on stdout.

### Fields → CLI (scaf/action_package/invoke/handler.py)

- `field` here is scaf's `field` with a `doc=` kwarg (the CLI help). Import: `from dataclasses import field` — scaf patches `doc`. Look at `scaf/user/discover/command.py` for the canonical example.
- No default → **required positional** arg.
- Has default → `--flag-name` optional (snake_case → slug-case). `bool` default → `store_true`.
- Custom typed fields are converted by a **fitter**: `fit_<field_name>` in a sibling `rules.py`, else metadata `fitter`, else type-based coercion (`get_fitter` in `scaf/tools.py`).

## The handler (handler.py)

```python
def handle(query: Show):
  ...  # may print to STDERR for progress/listings; NEVER stdout (reserved for JSON result)
  return result  # or None
```

## Locating the deck + aliases (common needs)

- Deck = nearest `.scaf/` folder. `LocateDeck` searches the start path's **parents** (not the path itself), so to include cwd pass `Path.cwd().resolve() / SCAF_FOLDER_NAME`:
  ```python
  deck = LocateDeck(path=Path.cwd().resolve() / SCAF_FOLDER_NAME).execute()
  ensure_import_path(deck)  # from scaf.user.call.handler — adds deck root to sys.path
  ```
- `deck.aliases_file`, `deck.root`, `deck.settings_file` are cached properties on `Deck`.

## User-facing commands

Put the action under `scaf/user/<name>/`. The CLI (`scaf/cli.py`) discovers everything under `scaf/user/` up to depth 2 and dispatches `scaf <name>`. Both `scaf <name>` and `scaf call scaf/user/<name>` reach the same package.

## TDD workflow (required by CLAUDE.md)

1. Write an integration test FIRST under `test/integration/user/tests/test_<name>.py` using the `sandbox` fixture (`test/integration/conftest.py`). `sandbox.scaf("<name>", *args)` runs the CLI in-process and returns `(success, stdout, stderr)`. Helpers: `sandbox.add_example_domain()`, `sandbox.scaf_init(depth)`, `sandbox.scaf("discover", ".")`.
2. Run it, confirm it FAILS for the right reason.
3. Implement until green.
4. `ruff check <paths> && ruff format --check <paths>`.

Reference implementation: `scaf/user/show/` (read-only query listing aliases without mutating the file).
