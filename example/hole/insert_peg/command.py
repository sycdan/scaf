from dataclasses import dataclass, field

from example.shape.entity import Shape


@dataclass
class InsertPeg:
  peg: Shape
  hole: Shape
  force_insert: bool = field(default=False, kw_only=True)
  """Bug 202601270041: Added underscore fields to test slug-case CLI conversion"""
