from dataclasses import dataclass


@dataclass
class TagRelease:
  """Tag the current HEAD with the version from scaf/__init__.py and push the tag.

  Idempotent - skips if HEAD is already tagged with the current version.
  """

  def execute(self) -> str:
    from dev.tag_release.handler import handle

    return handle(self)
