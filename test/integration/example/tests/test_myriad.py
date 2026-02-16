from uuid import UUID

from test.integration.conftest import Sandbox


def test_get_returns_expected_data(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call("example/myriad/get")

  assert success
  assert isinstance(data, dict)
  assert UUID(data["guid"])
  assert data["boolean"] is True
  assert data["integer"] == 42
  assert data["text"] == "hello"
  assert abs(data["float"] - 3.14) < 0.0001
