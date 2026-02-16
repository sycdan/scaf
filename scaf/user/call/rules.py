import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def fit_action(value: Path | str) -> Path:
  if isinstance(value, str):
    value = Path(value.strip())
  if not isinstance(value, Path):
    raise TypeError("must be a posix-compliant path")
  if value.as_posix() == ".":
    raise ValueError("must not be empty")
  return value
