"""Bug: datetime | None fields fail to parse CLI string arguments."""

from test.integration.conftest import Sandbox


def test_timestamps_ending_in_z_are_parsed(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/test_timestamp_handling",
    "--timestamp=2026-02-08T21:17:33Z",
  )

  assert success
  assert isinstance(data, dict)
  assert data["type_name"] == "datetime"
  assert not data["timestamp"].endswith("Z")


def test_datetime_optional_field_parses_space_separated(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/test_timestamp_handling",
    "--timestamp",
    "2026-02-20 14:30",
  )

  assert success
  assert isinstance(data, dict)
  assert data["timestamp"] is not None


def test_datetime_optional_field_parses_iso_offset(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/test_timestamp_handling",
    "--timestamp",
    "2026-02-23T15:30:00-04:00",
  )

  assert success
  assert isinstance(data, dict)
  assert data["timestamp"] is not None


def test_datetime_optional_field_defaults_to_none(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call("example/test_timestamp_handling")

  assert success
  assert isinstance(data, dict)
  assert data["timestamp"] is None
