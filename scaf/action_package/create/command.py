from dataclasses import dataclass, field
from pathlib import Path

from scaf.action_package.create.rules import fit_action, fit_description, fit_method
from scaf.deck.entity import Deck
from scaf.rules import values_must_fit


@dataclass
class CreateActionPackage:
  """Create a new domain action."""

  deck: Deck = field(
    doc="Which scaf deck to register the action with.",
  )
  action: Path = field(
    doc="Relative path to the action from the deck's root.",
    metadata={"fitter": fit_action},
  )
  method: str = field(
    doc="Either 'command' or 'query'.",
    default="command",
    metadata={"fitter": fit_method},
  )
  description: str = field(
    doc="What the action allows a user to do.",
    default="",
    metadata={"fitter": fit_description},
  )

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.action_package.create.handler import handle

    return handle(self)
