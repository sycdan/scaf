"""contains pure functions to validate and normalize user input"""

from pathlib import Path


def fit_action_path(value: Path | str) -> Path:
  if not value:
    raise ValueError("must not be empty")
  if not isinstance(value, Path):
    value = Path(value.strip())
  return value


def fit_action_method(value: str) -> str:
  valid_methods = {"command", "query"}
  value = value.strip().lower()
  if not value:
    raise ValueError("must not be empty")
  if value not in valid_methods:
    raise ValueError(f"must be one of {valid_methods}, got '{value}'")
  return value


def fit_description(value: str | None) -> str:
  if value is None:
    return ""
  clean_value = str(value).strip()
  if value and not clean_value:
    raise ValueError("must not be whitespace only")
  return clean_value
