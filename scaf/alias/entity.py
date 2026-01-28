from dataclasses import dataclass
from pathlib import Path


@dataclass
class Alias:
  name: str
  root: Path
  action: Path

  def __str__(self):
    return f"alias {self.name}='scaf {self.root.as_posix()} --call {self.action.as_posix()} --'"
