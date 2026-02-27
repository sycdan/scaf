"""Bug: running `scaf call --help` creates a --help action directory instead of returning help."""

from test.integration.conftest import Sandbox


def test_scaf_call_help_doesnt_create_directory(sandbox: Sandbox):
  sandbox.scaf_init()

  sandbox.scaf("call", "--help")

  assert not sandbox.exists("--help")
