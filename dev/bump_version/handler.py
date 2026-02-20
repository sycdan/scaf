import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dev.bump_version.command import BumpVersion
from dev.check.is_version_bump_needed.query import IsVersionBumpNeeded

logger = logging.getLogger(__name__)


def run_command(cmd, description):
  """Run a command and return success status.

  Args:
    cmd: List of command arguments (e.g., ['git', 'commit', '-m', 'message'])
    description: Human-readable description of the command
  """
  try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
      logger.error(f"❌ {description} failed:")
      logger.error(f"Command: {' '.join(cmd)}")
      logger.error(f"Error: {result.stderr}")
      logger.error(f"Output: {result.stdout}")
      return False
    return True
  except Exception as e:
    logger.error(f"{description} failed with exception: {e}")
    return False


def handle(command: BumpVersion) -> str:
  if not IsVersionBumpNeeded(remote_ref="refs/heads/main").execute():
    logger.info("Version bump is not needed")
    return "no change"

  # Get current date in YYYY.MM.DD format
  now = datetime.now(timezone.utc)
  date_version = now.strftime("%Y.%m.%d")

  # Find build number by checking if version already exists today
  init_file = Path("scaf/__init__.py")

  if not init_file.exists():
    raise FileNotFoundError("scaf/__init__.py not found")

  # Read current version
  with open(init_file, "r") as f:
    content = f.read()

  version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
  build_num = 1

  if version_match:
    current_version = version_match.group(1)
    # Check if it's already today's date
    if current_version.startswith(date_version):
      # Extract build number and increment
      if "." in current_version[len(date_version) :]:
        build_num = int(current_version.split(".")[-1]) + 1

  new_version = f"{date_version}.{build_num:04d}"

  # Update version in file
  new_content = re.sub(
    r'__version__ = ["\'][^"\']+["\']', f'__version__ = "{new_version}"', content
  )

  with open(init_file, "w", newline="") as f:
    f.write(new_content.strip() + "\n")

  run_command(["git", "add", "scaf/__init__.py"], "Staging version update")
  run_command(["git", "commit", "-m", "Bump version"], "Committing version update")
  run_command(
    ["git", "tag", "-a", new_version, "-m", f"Release {new_version}"],
    "Creating version tag",
  )

  print(f"✅ Version updated to {new_version}")
  return new_version
