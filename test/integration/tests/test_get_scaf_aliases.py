import pytest

from test.sandbox import Sandbox


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
  # automatically run tests *inside* the sandbox
  monkeypatch.chdir(tmp_path)
  return Sandbox(tmp_path)


@pytest.mark.integration
def test(sandbox: Sandbox):
  result = sandbox.run("scaf")
  aliases = result.stdout.splitlines()
  assert aliases
