from dataclasses import dataclass
from pathlib import Path

from scaf.core import Shape


@dataclass
class Alias(Shape):
  name: str
  action: Path
  root: Path

  def prepare(self):
    if not self.root.is_absolute():
      raise ValueError("root must be absolute")
    if self.action.is_absolute():
      raise ValueError("action must be relative")

  @classmethod
  def from_bash(cls, raw: str, root: Path) -> "Alias":
    # e.g.: alias domain.action='scaf call /home/mbd53/cyberdyne/skynet/up'
    if not raw.startswith("alias "):
      raise ValueError(f"Invalid alias format: {raw}")

    raw = raw[6:]
    name, scaf_command = raw.split("=", 1)
    scaf_command = scaf_command.strip("'\"")

    if not scaf_command.startswith("scaf call $DECK/"):
      raise ValueError(f"Invalid alias command: {scaf_command}")

    action = Path(scaf_command[16:])
    return cls(name=name, action=action, root=root)

  def to_bash(self) -> str:
    return f'alias {self.name}="scaf call $DECK/{self.action.as_posix()}"'

  def __str__(self):
    return self.name
