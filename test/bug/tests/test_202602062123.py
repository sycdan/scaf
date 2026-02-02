"""Bug: union types end up normalized to str."""

import uuid

from scaf import config


def test_union_type_is_normalized_to_first_option(sandbox):
  # This is the exact command that fails in the bug report
  result = sandbox.run_scaf(
    config.REPO_ROOT,
    "-vvv",
    "--call",
    "example/test_custom_union_types/",
    "--",
    f"entity_{uuid.uuid4().hex}",
  )

  # Should not fail due to unrecognized arguments
  assert result.returncode == 0, (
    f"Expected success but got error: {result.stdout}\n{result.stderr}"
  )
  assert "EntityRef" in result.stdout, (
    f"Expected type to be normalized to EntityRef, but got: {result.stdout}"
  )
