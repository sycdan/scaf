from dataclasses import dataclass


@dataclass
class IsVersionBumpNeeded:
  """Check if a version bump is needed when pushing to main."""

  def execute(self):
    from dev.check.is_version_bump_needed.handler import handle

    return handle(self)
