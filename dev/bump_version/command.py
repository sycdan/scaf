from dataclasses import dataclass


@dataclass
class BumpVersion:
  """Command to bump the app version using YYYY.MM.DD.NNNN format.

  Automatically increments build number for same-day versions.
  """

  dry_run: bool = False
  """If True, check if version bump is needed without actually doing it."""

  def execute(self) -> str:
    from dev.bump_version.handler import handle

    return handle(self)
