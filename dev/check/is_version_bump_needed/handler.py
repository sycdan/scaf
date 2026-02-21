import logging
import subprocess

from dev.check.is_version_bump_needed.query import IsVersionBumpNeeded

logger = logging.getLogger(__name__)

VERSION_FILE = "scaf/__init__.py"


def last_version_bump_commit() -> str | None:
  """Returns the SHA of the last commit that modified the version file, or None."""
  result = subprocess.run(
    ["git", "log", "-1", "--format=%H", "--", VERSION_FILE],
    capture_output=True,
    text=True,
  )
  if result.returncode != 0 or not result.stdout.strip():
    return None
  return result.stdout.strip()


def head_sha() -> str | None:
  result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
  if result.returncode != 0:
    return None
  return result.stdout.strip()


def has_changes_since(commit: str | None, domain: str) -> bool:
  domain_path = f"{domain}/"

  if not commit:
    # No previous bump — bump needed if scaf/ has any tracked files
    logger.info("No previous version bump found, checking if scaf/ has tracked files")
    result = subprocess.run(["git", "ls-files", domain_path], capture_output=True, text=True)
    return bool(result.stdout.strip())

  result = subprocess.run(
    ["git", "diff", "--name-only", f"{commit}..HEAD", domain_path],
    capture_output=True,
    text=True,
  )

  if result.returncode != 0:
    logger.warning(f"Failed to check for {domain_path} changes")
    return True  # Err on the side of caution

  has_changes = bool(result.stdout.strip())
  if has_changes:
    logger.info(f"Found changes in {domain_path} since last version bump ({commit[:7]})")
    for change in result.stdout.strip().split("\n"):
      if change:
        logger.info(f"  - {change}")
  else:
    logger.info(f"No changes in {domain_path} since last version bump ({commit[:7]})")

  return has_changes


def handle(query: IsVersionBumpNeeded) -> bool:
  if not query.remote_ref.endswith("/main"):
    logger.info("Not pushing to main branch, version bump not needed")
    return False

  last_bump = last_version_bump_commit()
  head = head_sha()

  if last_bump and last_bump == head:
    logger.info("HEAD is already a version bump commit, skipping")
    return False

  if not has_changes_since(last_bump, "scaf"):
    logger.info("No functional changes since last version bump, version bump not needed")
    return False

  logger.info("Functional changes detected since last version bump, version bump needed")
  return True
