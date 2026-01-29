from dataclasses import dataclass


@dataclass
class IsCodeFormatted:
  """Check if code passes ruff linting and formatting checks."""

  auto_fix: bool = False

  def execute(self):
    from dev.check.is_code_formatted.handler import handle

    return handle(self)
