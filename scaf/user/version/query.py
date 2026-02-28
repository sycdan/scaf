from dataclasses import dataclass

from scaf.core import Shape


@dataclass
class Version(Shape):
  """Print the current scaf version."""

  def execute(self):
    from scaf.user.version.handler import handle

    return handle(self)
