import json

from test.integration.conftest import Sandbox


def test_sets_string_prop(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, _, _ = sandbox.scaf(
    "config", "set", "example/project/backend/api", "host", "prod.example.com"
  )
  assert success

  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["project"]["backend"]["api"]["host"] == "prod.example.com"


def test_sets_int_prop_with_coercion(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, _, _ = sandbox.scaf("config", "set", "example/project/backend/api", "base", "/fake-api")
  assert success

  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["project"]["backend"]["api"]["base"] == "/fake-api"


def test_rejects_unknown_prop(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, _, _ = sandbox.scaf(
    "config", "set", "example/project/backend/api", "unknown_prop", "value"
  )
  assert not success


def test_rejects_invalid_value_for_type(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  success, _, _ = sandbox.scaf(
    "config", "set", "example/project/backend/api", "port", "not-a-number"
  )
  assert not success


def test_merges_with_existing_settings(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()
  sandbox.write(
    ".scaf/settings.json",
    '{"example": {"project": {"backend": {"api": {"host": "existing"}}}}, "other": "value"}',
  )

  success, _, _ = sandbox.scaf("config", "set", "example/project/backend/api", "port", "9090")
  assert success

  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["project"]["backend"]["api"]["host"] == "existing"  # preserved
  assert data["example"]["project"]["backend"]["api"]["port"] == 9090  # set
  assert data["other"] == "value"  # unrelated key preserved


def test_overwrites_existing_value(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  sandbox.write(
    ".scaf/settings.json", '{"example": {"project": {"backend": {"api": {"host": "old"}}}}}'
  )
  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["project"]["backend"]["api"]["host"] == "old"

  success, _, _ = sandbox.scaf("config", "set", "example/project/backend/api", "host", "new")
  assert success

  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["project"]["backend"]["api"]["host"] == "new"


def test_fails_without_deck(sandbox: Sandbox):
  success, _, _ = sandbox.scaf("config", "set", "example/project/backend/api", "host", "localhost")
  assert not success


def test_creates_settings_file_when_missing(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init()

  assert not sandbox.exists("example/myriad/settings.py")
  success, _, _ = sandbox.scaf("config", "set", "example/myriad", "fake", "value")
  assert success

  assert sandbox.exists("example/myriad/settings.py")
  content = sandbox.read("example/myriad/settings.py")
  assert "fake" in content

  data = json.loads(sandbox.read(".scaf/settings.json"))
  assert data["example"]["myriad"]["fake"] == "value"
