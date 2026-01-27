from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from scaf.action_package.entity import ActionPackage


@dataclass
class LoadActionPackage:
  action_path: Path
  """to the action directory or a handler file"""

  def __post_init__(self):
    self.action_path = Path(self.action_path)

  def execute(self) -> "ActionPackage":
    from scaf.action_package.load.handler import handle

    return handle(self)
