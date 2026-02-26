from dataclasses import dataclass, field

from scaf.core import Shape


@dataclass
class Init(Shape):
  """Configure the current directory as a Deck."""

  search_depth: int = field(
    default=3,
    doc="How many folder levels to search for actions when generating the aliases file.",
  )

  def execute(self):
    from scaf.user.init.handler import handle

    return handle(self)
