from dataclasses import dataclass


@dataclass
class BumpVersion:
  """Bump the app version prior to a release.

  Automatically increments build number for same-day versions.
  Idempotent - skips if HEAD is already a version bump commit.
  """

  def execute(self) -> str:
    from dev.bump_version.handler import handle

    return handle(self)
