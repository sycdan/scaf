import logging
import subprocess
import sys
from pathlib import Path

import pytest

from dev.test.command import Test

logger = logging.getLogger(__name__)

ACTION_DIR = Path(__file__).parent


def handle(command: Test, *things):
  logger.debug(f"Handling {command=}")
  pytest_args = ["--no-header", "--disable-warnings", "--tb=short", "-vvv", "-s"]
  if things:
    pytest_args += ["-k", " or ".join(things)]
    
  try:
    result = pytest.main(pytest_args)
    print(f"{result=}")
  except Exception as e:
    logger.error(f"Error running tests: {e}")
    return command.Result(success=False)

  logger.info("All tests passed")
  return command.Result(success=True)
