from dataclasses import dataclass


@dataclass
class BumpVersion:
  """Bump the app version during a release.

  Automatically increments build number for same-day versions.
  Creates a git tag for the version.
  Idempotent - skips if HEAD is already tagged with a version.
  """

  def execute(self) -> str:
    from dev.bump_version.handler import handle

    return handle(self)
