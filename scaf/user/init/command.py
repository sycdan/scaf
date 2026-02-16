from dataclasses import dataclass, field

from scaf.rules import values_must_fit


@dataclass
class Init:
  """Configure the current directory as a Deck."""

  search_depth: int = field(
    default=3,
    doc="How many folder levels to search for actions when generating the aliases file.",
  )

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.user.init.handler import handle

    return handle(self)
