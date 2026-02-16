from dataclasses import dataclass, field
from pathlib import Path

from scaf.action_package.load.rules import fit_action, fit_root
from scaf.rules import values_must_fit


@dataclass
class LoadActionPackage:
  root: Path = field(metadata={"fitter": fit_root})
  action: Path = field(metadata={"fitter": fit_action})

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.action_package.load.handler import handle

    return handle(self)
