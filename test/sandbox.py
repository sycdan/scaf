import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Sandbox:
  root: Path

  def chdir(self):
    os.chdir(self.root)

  def write(self, relpath: str, content: str):
    path = self.root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path

  def read(self, relpath: str) -> str:
    return (self.root / relpath).read_text()

  def exists(self, relpath: str) -> bool:
    return (self.root / relpath).exists()

  def run(self, *args, **kwargs):
    return subprocess.run(
      args,
      cwd=self.root,
      text=True,
      capture_output=True,
      **kwargs,
    )
