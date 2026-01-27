from pathlib import Path

from scaf import config
from scaf.action_package import rules as action_package


def ensure_absolute_path(path: Path | str) -> Path:
  path = Path(path)
  if not path.is_absolute():
    path = config.ROOT_DIR / path
  return path


def is_action_package(folder: Path) -> bool:
  try:
    filenames = [f.name for f in folder.iterdir()]
    action_package.must_contain_required_files(filenames)
    return True
  except ValueError:
    return False
