from dataclasses import dataclass


@dataclass
class IsWorkingDirClean:
  """Check if the git working directory is clean (no uncommitted changes)."""

  def execute(self):
    from dev.check.is_working_dir_clean.handler import handle

    return handle(self)
