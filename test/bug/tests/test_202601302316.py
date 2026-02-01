"""Bug test: unable to pass dynamic args to action."""

import json

from scaf import config


def test_pass_dynamic_args_example_action(sandbox):
  # This is the exact command that fails in the bug report
  result = sandbox.run_scaf(
    config.REPO_ROOT,
    "--call",
    "example/pass_dynamic_args/",
    "--",
    "init",
    "--with-flag",
  )

  # Should not fail due to unrecognized arguments
  assert result.returncode == 0, (
    f"Expected success but got error: {result.stdout}\n{result.stderr}"
  )
  assert "unrecognized arguments" not in result.stderr.lower()
  response = json.loads(result.stdout)
  assert "--with-flag" in response["args"]
