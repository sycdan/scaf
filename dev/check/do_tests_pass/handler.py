import logging

from dev.check.do_tests_pass.query import DoTestsPass
from dev.test.command import Test

logger = logging.getLogger(__name__)


def handle(query: DoTestsPass) -> bool:
  """Returns True if all tests pass using pytest."""

  return Test().execute().success
