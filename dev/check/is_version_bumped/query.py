from dataclasses import dataclass


@dataclass
class IsVersionBumped:
  """Check if a version bump is needed when pushing to main."""

  def execute(self):
    from dev.check.is_version_bumped.handler import handle

    return handle(self)
