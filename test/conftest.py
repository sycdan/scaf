import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from test.alias.entity import Alias


@dataclass
class Sandbox:
  root: Path
  scaf_prog_path = Path(__file__).parent.parent.parent / "scaf"

  def chdir(self) -> None:
    os.chdir(self.root)

  def write(self, relpath: str, content: str) -> Path:
    path = self.root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path

  def read(self, relpath: str) -> str:
    return (self.root / relpath).read_text()

  def exists(self, relpath: str) -> bool:
    return (self.root / relpath).exists()

  def run(self, *args, **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      args,
      cwd=self.root,
      text=True,
      capture_output=True,
      **kwargs,
    )

  def get_aliases(self, root: str = "") -> list[Alias]:
    result = self.run("scaf", root)
    raw_aliases = result.stdout.splitlines()
    aliases = [Alias.from_raw(alias) for alias in raw_aliases if alias.strip()]
    return aliases

  def run_scaf(self, *scaf_args) -> subprocess.CompletedProcess[str]:
    return self.run("scaf", *scaf_args)


@pytest.fixture
def sandbox(tmp_path, monkeypatch) -> Sandbox:
  # automatically run tests *inside* the sandbox
  monkeypatch.chdir(tmp_path)
  return Sandbox(tmp_path)
