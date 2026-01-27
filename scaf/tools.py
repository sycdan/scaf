"""May touch filesystem, but not DB or network."""

import os
import re
from hashlib import sha256
from pathlib import Path
from types import ModuleType


def ensure_init_files(code_dir: Path):
  """Ensure __init__.py files exist in all directories under code_dir."""
  for root, dirs, _ in os.walk(code_dir):
    for dir_name in dirs:
      init_file = Path(root) / dir_name / "__init__.py"
      init_file.touch(exist_ok=True)


def compute_hash(path: Path) -> str:
  return sha256(path.as_posix().encode("utf-8")).hexdigest()


def to_snake_case(name):
  # Insert underscores before capital letters (except at start)
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
  # Insert underscores before capital letters preceded by lowercase or digits
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
  # Replace any non-alphanumeric with underscores and clean up
  return re.sub(r"[^a-zA-Z0-9]+", "_", s2).strip("_").lower()


def to_camel_case(name):
  # First split on capital letters to handle CamelCase input
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", name)
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)
  # Then split on non-alphanumeric and capitalize each word
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", s2) if word)


def to_slug_case(name):
  # Insert hyphens before capital letters (except at start)
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
  # Insert hyphens before capital letters preceded by lowercase or digits
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1)
  # Replace any non-alphanumeric with hyphens and clean up
  return re.sub(r"[^a-zA-Z0-9]+", "-", s2).strip("-").lower()


def to_dot_path(path: Path):
  if path.as_posix() == ".":
    raise ValueError("Path cannot be empty")
  return ".".join(path.as_posix().split("/"))


def extract_first_dataclass(module: ModuleType) -> type:
  for name, obj in vars(module).items():
    if isinstance(obj, type) and not name.startswith("_"):
      if hasattr(obj, "__dataclass_fields__") and obj.__module__ == module.__name__:
        return obj
  raise ValueError(f"No dataclass found in {module.__file__}")


def resolve_path(action_path: Path | str) -> Path:
  if isinstance(action_path, str):
    action_path = Path(action_path)
  return action_path.resolve()


def find_available_actions(root_dir: Path) -> list[str]:
  actions = []
  for root, dirs, files in os.walk(root_dir):
    # Skip hidden directories and .venv, etc.
    dirs[:] = [d for d in dirs if not d.startswith(("."))]

    if "__init__.py" in files and "handler.py" in files:
      if "command.py" in files or "query.py" in files:
        actions.append(Path(root).relative_to(root_dir).as_posix())
  return sorted(actions)
