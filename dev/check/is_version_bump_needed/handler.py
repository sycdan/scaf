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


def has_changes_since_last_version_bump(domain: str) -> bool:
  domain_path = f"{domain}/"

  # Find the last version bump commit
  result = subprocess.run(
    [
      "git",
      "log",
      "--grep=^[0-9]\\{4\\}\\.[0-9]\\{2\\}\\.[0-9]\\{2\\}\\.[0-9]\\{4\\}$",
      "--pretty=%H",
      "-1",
    ],
    capture_output=True,
    text=True,
  )

  if result.returncode != 0 or not result.stdout.strip():
    # No previous version bump found, check if domain folder exists and has any files
    logger.info(
      f"No previous version bump commit found, checking if {domain_path} folder has content"
    )
    domain_result = subprocess.run(
      ["git", "ls-files", domain_path], capture_output=True, text=True
    )
    return bool(domain_result.stdout.strip())

  last_version_commit = result.stdout.strip()
  logger.info(f"Last version bump commit: {last_version_commit}")

  # Check for changes in domain folder since that commit
  changes_result = subprocess.run(
    ["git", "diff", "--name-only", last_version_commit + "..HEAD", domain_path],
    capture_output=True,
    text=True,
  )

  if changes_result.returncode != 0:
    logger.warning(f"Failed to check for {domain_path} changes")
    return True  # Err on the side of caution

  has_changes = bool(changes_result.stdout.strip())
  if has_changes:
    logger.info(f"Found changes in {domain_path} folder since last version bump")
    for change in changes_result.stdout.strip().split("\n"):
      if change:
        logger.info(f"  - {change}")
  else:
    logger.info(f"No changes in {domain_path} folder since last version bump")

  return has_changes


def handle(query: IsVersionBumpNeeded) -> bool:
  if last_commit_is_version_bump():
    logger.info("Last commit is a version bump, version bump not needed")
    return False

  if not query.remote_ref.endswith("/main"):
    logger.info("Not pushing to main branch, version bump not needed")
    return False

  if not has_changes_since_last_version_bump("scaf"):
    logger.info("No functional changes since last version bump, version bump not needed")
    return False

  logger.info("Functional changes detected since last version bump, version bump needed")
  return True
