import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Alias:
  name: str
  scaf_args: str

  @classmethod
  def from_raw(cls, raw: str) -> "Alias":
    # e.g.: alias scaf.call='scaf C:/Users/Dan/Projects/scaf/scaf/action/call'
    assert raw.startswith("alias "), f"Invalid alias format: {raw}"
    raw = raw[6:]
    name, command = raw.split("=", 1)
    command = command.strip("'\"")
    assert command.startswith("scaf "), f"Invalid alias command: {command}"
    command = command[5:]
    return cls(name=name, scaf_args=command)


@dataclass
class Sandbox:
  root: Path
  scaf_prog_path = Path(__file__).parent.parent.parent / "scaf"

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

  def get_aliases(self) -> list[Alias]:
    result = self.run("scaf")
    raw_aliases = result.stdout.splitlines()
    aliases = [Alias.from_raw(alias) for alias in raw_aliases if alias.strip()]
    return aliases

  def run_scaf(self, scaf_args: str) -> subprocess.CompletedProcess:
    return self.run("scaf", *(scaf_args.split()))
