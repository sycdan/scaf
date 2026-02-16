from dataclasses import dataclass, field
from pathlib import Path

from scaf.rules import values_must_fit
from scaf.user.call.rules import fit_action


@dataclass
class Call:
  """Invoke a domain action."""

  action: Path = field(
    doc="Absolute path to the action, e.g. '/home/mbd53/cyberdyne/skynet/up'",
    metadata={"fitter": fit_action},
  )

  def __post_init__(self):
    values_must_fit(self)

  def execute(self, *args):
    from scaf.user.call.handler import handle

    return handle(self, *args)
