from dataclasses import dataclass


@dataclass
class IsVersionBumpNeeded:
  """Check if the version needs to be updated when pushing to main."""

  local_ref: str = ""
  local_sha: str = ""
  remote_ref: str = ""
  remote_sha: str = ""

  def execute(self):
    from dev.check.is_version_bump_needed.handler import handle

    return handle(self)
