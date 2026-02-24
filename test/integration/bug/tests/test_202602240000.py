"""Bug: passing extra positional args to an action that doesn't accept them raises a cryptic TypeError."""

from test.integration.conftest import Sandbox


def test_extra_positional_args_gives_clear_error(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, data = sandbox.scaf_call(
    "example/myriad/get",
    "unexpected_extra_arg",
  )

  assert not success
