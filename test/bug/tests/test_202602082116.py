"""Bug: timestamps ending in Z are not seen as valid datetimes."""

from scaf import config


def test_timestamps_ending_in_z_are_allowed(sandbox):
  result = sandbox.run_scaf(
    config.REPO_ROOT,
    "-vvv",
    "--call",
    "example/test_timestamp_handling",
    "--",
    "2026-02-08T21:17:33Z",
  )

  assert result.returncode == 0, (
    f"Expected success but got error: {result.stdout}\n{result.stderr}"
  )
  assert "2026-02-08T21:17:33Z" in result.stdout
