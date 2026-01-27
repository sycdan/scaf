from dataclasses import dataclass


@dataclass
class Shape:
  sides: list[int]
  """defines the number and lengths of the sides of the shape"""

  def is_square(self) -> bool:
    from example.shape.rules import is_square

    return is_square(self.sides)
