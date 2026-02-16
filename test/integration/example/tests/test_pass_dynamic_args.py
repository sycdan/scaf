from test.integration.conftest import Sandbox


def test_pass_dynamic_args_example_action(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/pass_dynamic_args",
    "init",
    "--with-flag",
  )

  assert success
  assert isinstance(data, dict)
  assert "--with-flag" in data["extra_args"]
