from dataclasses import dataclass
from pathlib import Path

from scaf.action_package.entity import ActionPackage


@dataclass
class LoadActionPackage:
  root: Path
  """where the domain folder can be found"""
  action_folder: Path
  """must be importable from domain_root"""

  def __post_init__(self):
    self.root = Path(self.root)
    if not self.root.is_absolute():
      raise ValueError("root must be absolute")

    self.action_folder = Path(self.action_folder)
    if self.action_folder.is_absolute():
      raise ValueError("action_folder must be relative")

  def execute(self) -> ActionPackage:
    from scaf.action_package.load.handler import handle

    return handle(self)
