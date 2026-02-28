from dataclasses import dataclass

from example.thing.rules import is_round, is_square


@dataclass
class Thing:
  sides: list[int]
  """defines the number and lengths of the sides of the shape"""

  def is_square(self) -> bool:
    return is_square(self.sides)

  def is_round(self) -> bool:
    return is_round(self.sides)
