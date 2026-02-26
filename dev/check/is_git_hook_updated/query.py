from dataclasses import dataclass
from pathlib import Path

from scaf.core import Shape


@dataclass
class IsGitHookUpdated(Shape):
  """Check if the installed git hook matches the source version."""

  hook_file: Path

  def execute(self):
    from dev.check.is_git_hook_updated.handler import handle

    return handle(self)
