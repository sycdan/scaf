from dataclasses import dataclass
from pathlib import Path

from scaf.alias.entity import Alias


@dataclass
class GetAliases:
  root: Path
  filter: str = ""
  """only return aliases for actions starting with this"""

  def __post_init__(self):
    self.root = Path(self.root)
    if not self.root.is_absolute():
      raise ValueError("root must be absolute")

  def execute(self) -> list[Alias]:
    from scaf.core.get_aliases.handler import handle

    return handle(self)
