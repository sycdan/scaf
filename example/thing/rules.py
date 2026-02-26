def is_round(sides: list[int]) -> bool:
  return len(sides) == 1


def is_square(sides: list[int]) -> bool:
  return len(sides) == 4 and all(side == sides[0] for side in sides)
