from dataclasses import dataclass


@dataclass
class BumpVersion:
  """Command to bump the app version using YYYY.MM.DD.NNNN format.

  Automatically increments build number for same-day versions.
  Idempotent - skips if last commit is already a version bump.
  """

  def execute(self) -> str:
    from dev.bump_version.handler import handle

    return handle(self)
