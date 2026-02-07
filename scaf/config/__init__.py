import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

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
  logger.debug(f"{ROOT_DIR=}")


def configure_logging(verbosity: int):
  if verbosity >= 3:
    level = logging.DEBUG
    format = "%(asctime)s %(levelname)s %(message)s [%(name)s]"
  elif verbosity == 2:
    level = logging.INFO
    format = "%(levelname)s %(message)s"
  elif verbosity == 1:
    level = logging.WARNING
    format = "%(levelname)s %(message)s"
  else:
    level = logging.ERROR
    format = "%(levelname)s %(message)s"

  logging.addLevelName(logging.DEBUG, "🐛")
  logging.addLevelName(logging.INFO, "ℹ️ ")
  logging.addLevelName(logging.WARNING, "⚠️ ")
  logging.addLevelName(logging.ERROR, "❌")

  logging.basicConfig(
    level=level,
    format=format,
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
  )
