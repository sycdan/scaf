from dataclasses import dataclass, field

from scaf.alias.entity import Alias
from scaf.core import Shape
from scaf.deck.entity import Deck


@dataclass
class Discover(Shape):
  """Return aliases for all valid domain actions visible from a given deck."""

  deck: Deck = field(
    doc="where to search from",
  )
  depth: int = field(
    doc="recurse this many levels while searching for actions",
    default=5,
  )
  filter: str = field(
    doc="return only aliases starting with this glob pattern (e.g. 'mydomain/*')",
    default="",
  )
  user: bool = field(
    doc="exit with code 0 after printing the listing (instead of returning it to the caller)",
    default=True,
  )

  @dataclass
  class Result:
    aliases: list[Alias]

  def execute(self):
    from scaf.user.discover.handler import handle

    return handle(self)
