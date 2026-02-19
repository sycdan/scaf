from pathlib import Path

AND = "AND"
OR = "OR"


def is_capable_entity(action: Path) -> bool:
  """Return True if the action represents an operation on a capable entity.

  An action is 'capable' when its name is a single word (no underscores),
  e.g. `load`, `get`, `launch`. In that case the immediate parent folder
  is treated as the capable entity and deserves an entity.py.
  """
  return "_" not in action.name and len(action.parts) >= 2


def must_contain_required_files(filenames: list[str] | set[str]) -> None:
  """purely validates that all required domain action files are present"""
  filenames = set(filenames)

  rules = [
    (AND, ["__init__.py", "handler.py"]),
    (OR, ["command.py", "query.py"]),
  ]

  missing = []
  for mode, files in rules:
    if mode == AND:
      missing.extend(f for f in files if f not in filenames)
    elif mode == OR:
      if not any(f in filenames for f in files):
        missing.append(" or ".join(files))

  if missing:
    raise ValueError(f"Invalid action package.\nMissing: {', '.join(missing)}")
