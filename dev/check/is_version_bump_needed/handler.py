import logging
import os
import re
import subprocess
import sys
import traceback

from dev.check.is_version_bumped.query import IsVersionBumped

logger = logging.getLogger(__name__)


def handle(query: IsVersionBumped) -> bool:
  """Returns True if version has been bumped (last commit is a version bump)."""

  try:
    # Check if the last commit was already a version bump
    result = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True, text=True)
    if result.returncode == 0:
      last_commit_msg = result.stdout.strip()
      # Check if it matches version format YYYY.MM.DD.NNNN
      if re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", last_commit_msg):
        logger.info("Version is up to date: %s", last_commit_msg)
        return True

    logger.error("Version bump is required before pushing to main")
    print("💡 Run dev.bump-version")
    return False
  except Exception as e:
    print(f"Version check failed: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    traceback.print_exc()
    return False
