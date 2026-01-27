---
applyTo: "**/*.py"
---

# Python Script Standards (must be followed exactly)

## Coding Style

- Refer to `pyproject.toml` for ruff configuration and follow those formatting & linting rules.
- All imports should be placed at the top of the file, except in special cases where doing so causes problems (e.g a circular dependency).
- Do add return type hints to function definitions.
- Do add type hints for function parameters.
- Do add type hints when defining empty local arrays that will be returned from functions.

## Additional Rules

- Executable Python scripts must have a shebang line: `#!/usr/bin/env python` and be marked as executable.
- When running pytest, prefix the command with `PYTHONPATH=. ` to ensure the root directory is included in the module search path.
- Use `@dataclass` to define domain entities & request/response shapes, unless there is a specific reason not to.
