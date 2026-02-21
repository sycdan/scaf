from pathlib import Path


def fit_path(value: Path) -> Path:
  if not isinstance(value, Path):
    raise TypeError("must be a Path")
  return value
