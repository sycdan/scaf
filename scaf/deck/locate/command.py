from dataclasses import dataclass, field
from pathlib import Path

from scaf.deck.locate.rules import fit_path
from scaf.rules import values_must_fit


@dataclass
class LocateDeck:
  """Find the nearest Deck to a given path."""

  path: Path = field(
    metadata={"fitter": fit_path},
    doc="An absolute or relative path to start searching from.",
  )

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.deck.locate.handler import handle

    return handle(self)
