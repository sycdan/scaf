from dataclasses import dataclass
from pathlib import Path


@dataclass
class GetAliases:
  root: Path

  def __post_init__(self):
    self.root = Path(self.root)
    if not self.root.is_absolute():
      raise ValueError("root must be absolute")

  def execute(self):
    from scaf.core.get_aliases.handler import handle

    return handle(self)
