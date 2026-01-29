import logging
import subprocess
import sys

from dev.check.do_tests_pass.query import DoTestsPass

logger = logging.getLogger(__name__)


def handle(query: DoTestsPass) -> bool:
  """Returns True if all tests pass using pytest."""

  result = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True)

  if result.returncode != 0:
    print("Tests failed:")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    return False

  logger.info("All tests passed")
  return True
