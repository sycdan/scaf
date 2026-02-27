from dataclasses import dataclass, field
from pathlib import Path

from scaf.core import Shape
from scaf.user.call.rules import fit_action


@dataclass
class Call(Shape):
  """Invoke a domain action."""

  action: Path = field(
    doc="Absolute path to the action, e.g. '/home/mbd53/cyberdyne/skynet/up'",
    metadata={"fitter": fit_action},
  )
  args: list[str] = field(default_factory=list, doc="Arguments to pass to the action.")

  def execute(self):
    from scaf.user.call.handler import handle

    return handle(self)
