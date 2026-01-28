import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from bump_version.command import BumpVersion


def run_command(cmd, description):
  """Run a shell command and return success status."""
  try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
      print(f"❌ {description} failed:")
      print(f"Command: {cmd}")
      print(f"Error: {result.stderr}")
      print(f"Output: {result.stdout}")
      return False
    return True
  except Exception as e:
    print(f"❌ {description} failed with exception: {e}")
    return False


def handle(command: BumpVersion) -> str:
  """Update version in scaf/__init__.py with current date format.

  Returns the new version string. Idempotent - skips bump if last commit was a version bump.
  In dry-run mode, returns 'NEEDS_BUMP' if bump is needed, otherwise returns current version.
  """
  # Check if the last commit was already a version bump
  result = subprocess.run(["git", "log", "-1", "--pretty=%s"], capture_output=True, text=True)
  if result.returncode == 0:
    last_commit_msg = result.stdout.strip()
    # Check if it matches version format YYYY.MM.DD.NNNN
    if re.match(r"^\d{4}\.\d{2}\.\d{2}\.\d{4}$", last_commit_msg):
      if command.dry_run:
        print(f"ℹ️  Last commit was already a version bump: {last_commit_msg}")
        return last_commit_msg
      print(f"ℹ️  Last commit was already a version bump: {last_commit_msg}")
      print("✅ Skipping version update")
      return last_commit_msg

  # If we get here, a bump is needed
  if command.dry_run:
    print("⚠️  Version bump is needed")
    return "NEEDS_BUMP"

  print("📝 Updating version...")

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

  with open(init_file, "w") as f:
    f.write(new_content)

  run_command("git add scaf/__init__.py", "Staging version update")
  run_command(f"git commit -m {shlex.quote(new_version)}", "Committing version update")

  print(f"✅ Version updated to {new_version}")
  return new_version
