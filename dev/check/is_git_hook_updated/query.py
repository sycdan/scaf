from dataclasses import dataclass
from pathlib import Path


@dataclass
class IsGitHookUpdated:
  """Check if the installed git hook matches the source version."""

  hook_file: Path

  def __post_init__(self):
    self.hook_file = Path(self.hook_file)

  def execute(self):
    from dev.check.is_git_hook_updated.handler import handle

    return handle(self)
