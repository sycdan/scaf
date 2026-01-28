import pytest

from test.sandbox import Sandbox


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
  # automatically run tests *inside* the sandbox
  monkeypatch.chdir(tmp_path)
  return Sandbox(tmp_path)


@pytest.mark.integration
def test(sandbox: Sandbox):
  aliases = sandbox.get_aliases()
  create_action = next((a for a in aliases if a.name == "scaf.create-action"), None)
  assert create_action is not None
  result = sandbox.run_scaf(create_action.scaf_args + " my_action")
  # this should fail as we did not provide all required args to create the action
  assert result.returncode == 1
