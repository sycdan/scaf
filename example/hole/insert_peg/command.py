from dataclasses import dataclass, field

from example.thing.entity import Thing
from scaf.core import Shape


@dataclass
class InsertPeg(Shape):
  """Put the thing in the thing."""

  peg: Thing = field(doc="The shape of the peg to insert.")
  hole: Thing = field(doc="The shape of the hole to insert the peg into.")
  force: bool = field(default=False, kw_only=True, doc="Push harder.")

  @dataclass
  class Result:
    success: bool = field(doc="Whether the peg was successfully inserted.")

  def execute(self) -> Result:
    from example.hole.insert_peg.handler import handle

    return handle(self)
