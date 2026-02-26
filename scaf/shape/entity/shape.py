from dataclasses import dataclass

from scaf.rules import values_must_fit


@dataclass
class Shape:
  """Base class for dataclasses that define the structure of domain actions."""

  def __post_init__(self):
    values_must_fit(self)
    if prepare := getattr(type(self), "prepare", None):
      prepare(self)
