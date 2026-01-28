from dataclasses import dataclass


@dataclass
class DoTestsPass:
  """Check if all tests pass using pytest."""

  def execute(self):
    from dev.check.do_tests_pass.handler import handle

    return handle(self)
