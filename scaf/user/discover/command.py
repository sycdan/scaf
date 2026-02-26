from dataclasses import dataclass, field

from scaf.alias.entity import Alias
from scaf.deck.entity import Deck
from scaf.core import Shape


@dataclass
class Discover(Shape):
  """Return aliases for all valid domain actions visible from a given deck."""

  deck: Deck = field(
    doc="Where to search from.",
  )
  depth: int = field(
    doc="How many levels of sub-folders to search for actions.",
    default=5,
  )
  filter: str = field(
    doc="Only return aliases for actions starting with this glob pattern.",
    default="",
  )

  @dataclass
  class Result:
    aliases: list[Alias]

  def execute(self):
    from scaf.user.discover.handler import handle

    return handle(self)
