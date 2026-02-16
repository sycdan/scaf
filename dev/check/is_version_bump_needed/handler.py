import logging
import re
import subprocess

from dev.check.is_version_bump_needed.query import IsVersionBumpNeeded

logger = logging.getLogger(__name__)


def last_commit_is_version_bump() -> bool:
  """Returns true if HEAD has a version tag."""
  result = subprocess.run(["git", "tag", "--points-at", "HEAD"], capture_output=True, text=True)
  if result.returncode:
    logger.warning("Failed to get tags at HEAD")
    return False

  tags = result.stdout.strip().split("\n") if result.stdout.strip() else []

  for tag in tags:
    if re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", tag):
      return True

  return False


def has_changes_since_last_version_bump(domain: str) -> bool:
  domain_path = f"{domain}/"

  # Find the last version tag (tags matching YYYY.MM.DD.NNNN format)
  result = subprocess.run(
    ["git", "tag", "--list", "--sort=-version:refname"],
    capture_output=True,
    text=True,
  )

  if result.returncode != 0:
    logger.warning("Failed to list tags")
    return True  # Err on the side of caution

  # Find the first tag matching version format
  last_version_tag = None
  if result.stdout.strip():
    for tag in result.stdout.strip().split("\n"):
      if re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", tag):
        last_version_tag = tag
        break

  if not last_version_tag:
    # No previous version tag found, check if domain folder exists and has any files
    logger.info(f"No previous version tag found, checking if {domain_path} folder has content")
    domain_result = subprocess.run(
      ["git", "ls-files", domain_path], capture_output=True, text=True
    )
    return bool(domain_result.stdout.strip())

  logger.info(f"Last version tag: {last_version_tag}")

  # Check for changes in domain folder since that tag
  changes_result = subprocess.run(
    ["git", "diff", "--name-only", last_version_tag + "..HEAD", domain_path],
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
    logger.info("HEAD is tagged with a version, version bump not needed")
    return False

  if not query.remote_ref.endswith("/main"):
    logger.info("Not pushing to main branch, version bump not needed")
    return False

  if not has_changes_since_last_version_bump("scaf"):
    logger.info("No functional changes since last version bump, version bump not needed")
    return False

  logger.info("Functional changes detected since last version bump, version bump needed")
  return True
