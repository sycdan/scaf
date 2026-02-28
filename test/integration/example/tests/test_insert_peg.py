from test.integration.conftest import Sandbox


def test_rules_module_fitter_is_used_automatically(sandbox: Sandbox):
  """fit_peg and fit_hole in insert_peg/rules.py should be picked up by get_fitter
  without any explicit metadata={"fitter": ...} on the command fields."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  # Pass peg and hole as comma-separated strings; rules.py fitters should parse them
  success, data = sandbox.scaf_call("example/hole/insert_peg", "4,4,4,4", "3,3,5")

  assert success, f"Expected insert_peg to succeed, got: {data}"
  assert data["peg"] == {"sides": [4, 4, 4, 4]}, f"Unexpected peg: {data['peg']}"
  assert data["hole"] == {"sides": [3, 3, 5]}, f"Unexpected hole: {data['hole']}"
  assert data["force_insert"] is False
