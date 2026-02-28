from dataclasses import dataclass, field

from scaf.core import Shape
from scaf.deck.entity import Deck


@dataclass
class Serve(Shape):
  """Start a local dev API server for testing domain actions via a browser UI."""

  deck: Deck = field(
    doc="Path to the scaf deck to serve actions from.",
  )
  port: int = field(
    default=54545,
    doc="Port number to listen on.",
  )

  def execute(self):
    from scaf.user.serve.handler import handle

    return handle(self)
