"""CLI commands are discovered dynamically from scaf/user/ instead of being hardcoded."""

from test.integration.conftest import Sandbox


def test_discover_is_available_as_cli_command(sandbox: Sandbox):
  """scaf discover should be callable; it's a user action, not hardcoded in cli choices."""
  success, stdout, stderr = sandbox.scaf("discover", "--help")
  assert success


def test_version_command_prints_version(sandbox: Sandbox):
  import scaf

  success, stdout, stderr = sandbox.scaf("version")
  assert success
  assert scaf.__version__ in stdout
