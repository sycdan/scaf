import logging
import subprocess
import sys

from dev.check.is_code_formatted.query import IsCodeFormatted

logger = logging.getLogger(__name__)


def handle(query: IsCodeFormatted) -> bool:
  """Returns True if code passes ruff linting and formatting checks."""

  if query.auto_fix:
    logger.info("Auto-fixing ruff issues...")
    subprocess.run(
      [sys.executable, "-m", "ruff", "check", "--fix", "."], capture_output=True, text=True
    )
    subprocess.run([sys.executable, "-m", "ruff", "format", "."], capture_output=True, text=True)

    # Check if any files were modified by ruff
    git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if git_status.stdout.strip():
      logger.info("Auto-fixed ruff issues, committing changes...")
      subprocess.run(["git", "add", "."], check=True)
      subprocess.run(["git", "commit", "-m", "Auto-fix ruff linting issues"], check=True)

  # Run final checks
  lint_result = subprocess.run(
    [sys.executable, "-m", "ruff", "check", "."], capture_output=True, text=True
  )
  if lint_result.returncode != 0:
    print("Ruff linting failed:")
    print(f"stdout: {lint_result.stdout}")
    print(f"stderr: {lint_result.stderr}")
    print(f"returncode: {lint_result.returncode}")
    return False

  format_result = subprocess.run(
    [sys.executable, "-m", "ruff", "format", "--check", "."], capture_output=True, text=True
  )
  if format_result.returncode != 0:
    logger.error("Ruff formatting check failed:")
    logger.error(format_result.stdout)
    return False

  logger.info("Code passes all ruff checks")
  return True
