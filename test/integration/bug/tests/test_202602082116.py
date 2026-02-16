"""Bug: timestamps ending in Z are not seen as valid datetimes."""

from test.integration.conftest import Sandbox


def test_timestamps_ending_in_z_are_allowed(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/test_timestamp_handling",
    "2026-02-08T21:17:33Z",
  )

  assert success
  assert isinstance(data, dict)
  assert data["type_name"] == "str"
  assert data["timestamp"] == "2026-02-08T21:17:33Z"
