from dataclasses import dataclass, field

from example.thing.entity import Thing


@dataclass
class InsertPeg:
  peg: Thing
  hole: Thing
  force_insert: bool = field(default=False, kw_only=True)
  """Bug 202601270041: Added underscore fields to test slug-case CLI conversion"""
