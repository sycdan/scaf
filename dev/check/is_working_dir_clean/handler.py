import logging
import subprocess

from dev.check.is_working_dir_clean.query import IsWorkingDirClean

logger = logging.getLogger(__name__)


def handle(query: IsWorkingDirClean) -> bool:
  """Returns True if the git working directory is clean (no uncommitted changes)."""

  result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

  if result.returncode != 0:
    logger.error("Failed to check git status")
    return False

  if result.stdout.strip():
    logger.warning("Git working directory is not clean")
    logger.debug(f"{result.stdout=}")
    return False

  logger.info("Git working directory is clean")
  return True
