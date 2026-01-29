import logging
import re
import subprocess

from dev.check.is_version_bump_needed.query import IsVersionBumpNeeded

logger = logging.getLogger(__name__)


def last_commit_is_version_bump() -> bool:
  result = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True, text=True)
  if result.returncode:
    logger.warning("Failed to get last commit")
    return False

  last_commit_msg = result.stdout.strip()
  # Check if it matches version format YYYY.MM.DD.NNNN
  if re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", last_commit_msg):
    logger.info("Version is up to date: %s", last_commit_msg)
    return True

  return False


def handle(query: IsVersionBumpNeeded) -> bool:
  if last_commit_is_version_bump():
    return False

  if query.remote_ref.endswith("/main"):
    logger.info("Version bump is required before pushing to main")
    return True

  return False
