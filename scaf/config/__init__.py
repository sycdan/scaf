import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent


def set_root_dir(path: Path | str):
  global ROOT_DIR
  ROOT_DIR = Path(path)
  sys.path.insert(0, str(ROOT_DIR))


DEBUG = os.getenv("SCAF_DEBUG", "0") == "1"
