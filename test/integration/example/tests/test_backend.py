import pytest

from scaf.config import SCAF_FOLDER_NAME
from test.integration.conftest import Sandbox


def test_new_action_is_aliased_in_nested_deck(sandbox: Sandbox):
  # Copy the example domain into the sandbox so we have some actions to work with
  sandbox.add_example_domain()
  backend_domain = "example/project/backend"
  backend_action = "api/serve"
  root_action_path = f"{backend_domain}/{backend_action}"

  assert not sandbox.exists(SCAF_FOLDER_NAME)
  sandbox.scaf_init(5)
  assert sandbox.exists(SCAF_FOLDER_NAME)
  pytest.raises(AssertionError, lambda: sandbox.ensure_aliased(root_action_path))
  pytest.raises(AssertionError, lambda: sandbox.ensure_aliased(backend_action))

  # Set up a scaf deck in the backend directory
  backend_root = sandbox.chdir(backend_domain)
  assert not sandbox.exists(backend_root / SCAF_FOLDER_NAME)
  sandbox.scaf_init(3)
  assert sandbox.exists(backend_root / SCAF_FOLDER_NAME)
  alias = sandbox.ensure_aliased(backend_action, backend_root)
  assert alias.name == "api.serve", "Expected alias name to be relative to backend"
