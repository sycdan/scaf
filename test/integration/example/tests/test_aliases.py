from test.integration.conftest import Sandbox


def test_expected_aliases_are_exposed(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init(5)

  for expected in [
    ("example/custom_union_types", "example.custom-union-types"),
    ("example/hole/insert_peg", "example.hole.insert-peg"),
    ("example/myriad/get", "example.myriad.get"),
    ("example/pass_dynamic_args", "example.pass-dynamic-args"),
    ("example/test_timestamp_handling", "example.test-timestamp-handling"),
  ]:
    alias = sandbox.ensure_aliased(expected[0])
    assert alias.name == expected[1], f"Expected alias '{expected[1]}' to be defined"
