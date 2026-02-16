import uuid

from test.integration.conftest import Sandbox


def test_union_type_is_normalized_to_first_option(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()
  guid = uuid.uuid4().hex

  success, data = sandbox.scaf_call(
    "example/custom_union_types",
    f"entity_{guid}",
  )

  assert success
  assert isinstance(data, dict)
  assert data["type_name"] == "EntityRef"
  assert isinstance(data["entity"], dict)
  assert data["entity"]["key"] == f"entity_{guid}"
