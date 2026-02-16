from pathlib import Path


def fit_root(value: Path):
  if not value.is_absolute():
    raise ValueError("must be absolute")
  return value


def fit_action(value: Path):
  if value.is_absolute():
    raise ValueError("must be relative")
  return value
