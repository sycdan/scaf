import logging
import re
import subprocess
from pathlib import Path

from dev.tag_release.command import TagRelease

logger = logging.getLogger(__name__)

VERSION_FILE = "scaf/__init__.py"


def current_version() -> str:
  content = Path(VERSION_FILE).read_text()
  match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
  if not match:
    raise ValueError(f"Could not find __version__ in {VERSION_FILE}")
  return match.group(1)


def last_version_bump_commit() -> str | None:
  """Returns the SHA of the last commit that modified the version file, or None."""
  result = subprocess.run(
    ["git", "log", "-1", "--format=%H", "--", VERSION_FILE],
    capture_output=True,
    text=True,
    encoding="utf-8",
  )
  if result.returncode != 0 or not result.stdout.strip():
    return None
  return result.stdout.strip()


def tag_exists_at(version: str, commit: str) -> bool:
  """Returns True if the tag exists and points to the expected commit. Raises if it points elsewhere."""
  exists = subprocess.run(
    ["git", "tag", "--list", version],
    capture_output=True,
    text=True,
    encoding="utf-8",
  )
  if not exists.stdout.strip():
    return False

  points_to = subprocess.run(
    ["git", "rev-parse", f"{version}^{{}}"],
    capture_output=True,
    text=True,
    encoding="utf-8",
  )
  tagged_commit = points_to.stdout.strip()
  if tagged_commit != commit:
    raise RuntimeError(
      f"Tag {version} already exists but points to {tagged_commit[:7]}, expected {commit[:7]}"
    )
  return True


def run(cmd, description):
  result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
  if result.returncode != 0:
    logger.error(f"❌ {description} failed:")
    logger.error(f"Command: {' '.join(cmd)}")
    logger.error(f"Error: {result.stderr}")
    raise RuntimeError(f"{description} failed")


def handle(command: TagRelease) -> str:
  bump_commit = last_version_bump_commit()
  if not bump_commit:
    raise RuntimeError(f"No version bump commit found (no commits touch {VERSION_FILE})")

  version = current_version()

  if tag_exists_at(version, bump_commit):
    logger.info(f"{bump_commit[:7]} is already tagged {version}, skipping")
    return "no change"

  run(["git", "tag", "-a", version, bump_commit, "-m", f"Release {version}"], "Creating tag")
  run(["git", "push", "origin", version], "Pushing tag")

  print(f"✅ Tagged {bump_commit[:7]} as {version}")
  return version
