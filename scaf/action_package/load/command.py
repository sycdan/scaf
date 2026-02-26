from dataclasses import dataclass, field
from pathlib import Path

from scaf.action_package.load.rules import fit_action, fit_root
from scaf.core import Shape


@dataclass
class LoadActionPackage(Shape):
  root: Path = field(metadata={"fitter": fit_root})
  action: Path = field(metadata={"fitter": fit_action})

  def execute(self):
    from scaf.action_package.load.handler import handle

    return handle(self)
