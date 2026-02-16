import io
import json
import os
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

import pytest

from scaf.alias.entity import Alias
from scaf.config import ALIASES_FILENAME, REPO_ROOT, SCAF_FOLDER_NAME

pytestmark = pytest.mark.integration


@dataclass
class Sandbox:
  root: Path

  def chdir(self, relpath: Path | str | None = None) -> Path:
    if relpath is None:
      relpath = Path(".")
    elif not isinstance(relpath, Path):
      relpath = Path(relpath)
    if relpath.is_absolute():
      raise ValueError("Path must be relative")

    path = self.root / relpath
    path.mkdir(parents=True, exist_ok=True)
    os.chdir(path)
    return path.relative_to(self.root)

  def write(self, relpath: str, content: str) -> Path:
    path = self.root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path

  def read(self, relpath: Path | str) -> str:
    if isinstance(relpath, Path):
      relpath = relpath.as_posix()
    return (self.root / relpath).read_text()

  def exists(self, relpath: Path | str) -> bool:
    if isinstance(relpath, Path):
      relpath = relpath.as_posix()
    return (self.root / relpath).exists()

  def run(self, *args, **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      args,
      cwd=self.root,
      text=True,
      capture_output=True,
      encoding="utf-8",
      **kwargs,
    )

  def get_aliases(self, scaf_root: Path | None = None) -> list[Alias]:
    scaf_root = scaf_root or Path(".")
    aliases = []
    content = self.read(scaf_root / SCAF_FOLDER_NAME / ALIASES_FILENAME)
    raw_aliases = reversed(content.splitlines())  # Actual aliases are at the bottom
    for raw_alias in raw_aliases:
      try:
        aliases.append(Alias.from_bash(raw_alias, root=self.root / scaf_root))
      except ValueError:
        break
    return aliases

  def ensure_aliased(self, action: str, scaf_root: Path | None = None) -> Alias:
    aliases = self.get_aliases(scaf_root)
    action_posix = Path(action).as_posix()
    for alias in aliases:
      if alias.action.as_posix() == action_posix:
        return alias
    assert False, (
      f"Alias for action '{action}' not found in {scaf_root} (searched {len(aliases)} aliases)"
    )

  def _scaf(self, *args):
    from scaf.cli import main

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
      try:
        main(args)
        success = True
      except SystemExit as e:
        success = e.code == 0

    return success, stdout.getvalue(), stderr.getvalue()

  def scaf_init(self, search_depth: int = 0):
    result = self._scaf("init", str(search_depth))
    return result[0]

  def scaf_call(self, action: Path | str, *action_args):
    """Call an action with scaf and return the parsed JSON output."""
    if isinstance(action, Path):
      action = action.as_posix()
    result = self._scaf("call", action, *action_args)
    output = result[1]
    if output.strip():
      return result[0], json.loads(output)
    return result[0], None

  def add_example_domain(self):
    """Copy the example domain into the sandbox."""
    example_domain_path = REPO_ROOT / "example"
    example_domain_path.copy_into(self.root)


@pytest.fixture
def sandbox(tmp_path, monkeypatch) -> Sandbox:
  """Configures a temporary directory as the project root for testing."""
  monkeypatch.chdir(tmp_path)
  return Sandbox(tmp_path)
