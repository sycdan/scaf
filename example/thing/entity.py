from dataclasses import dataclass


@dataclass
class Thing:
  sides: list[int]
  """defines the number and lengths of the sides of the shape"""

  def is_square(self) -> bool:
    from example.thing.rules import is_square

    return is_square(self.sides)
