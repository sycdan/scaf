import os
import sys
from pathlib import Path

DEBUG = os.getenv("SCAF_DEBUG", "0") == "1"
REPO_ROOT = Path(__file__).parent.parent.parent
"""for internal use only -- should never change"""
ROOT_DIR = Path(__file__).parent.parent.parent
"""the level above the working domain folder"""


def set_root_dir(path: Path | str):
  global ROOT_DIR
  ROOT_DIR = Path(path)
  if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
  if DEBUG:
    print(f"{ROOT_DIR=}", file=sys.stderr)
