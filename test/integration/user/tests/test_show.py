from scaf.config import ALIASES_FILENAME, SCAF_FOLDER_NAME
from test.integration.conftest import Sandbox

RED = "\033[0;31m"


def _aliases_file(sandbox: Sandbox):
  return sandbox.root / SCAF_FOLDER_NAME / ALIASES_FILENAME


def test_show_lists_aliases_in_red(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init(0)
  sandbox.scaf("discover", ".")  # populate aliases file

  success, stdout, stderr = sandbox.scaf("show")
  assert success, f"Expected show to succeed\nstdout={stdout}\nstderr={stderr}"

  for name in ["example.custom-union-types", "example.myriad.get"]:
    assert RED + name in stderr, f"Expected '{name}' in red in stderr\nstderr={stderr}"


def test_show_does_not_mutate_aliases_file(sandbox: Sandbox):
  """Unlike discover, show is read-only: a not-yet-aliased action stays absent."""
  sandbox.scaf_init(0)  # empty aliases file
  sandbox.add_example_domain()  # actions exist on disk but are NOT in the aliases file

  before = _aliases_file(sandbox).read_text(encoding="utf-8")

  success, stdout, stderr = sandbox.scaf("show")
  assert success, f"Expected show to succeed\nstdout={stdout}\nstderr={stderr}"

  after = _aliases_file(sandbox).read_text(encoding="utf-8")
  assert before == after, "show must not mutate the aliases file"
