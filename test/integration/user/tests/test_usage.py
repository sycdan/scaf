# action_path, expected_alias
from pathlib import Path

from test.integration.conftest import Sandbox


def test_happy_path(sandbox: Sandbox):
  sandbox.scaf_init()

  # Call a non-existent action; this should cause the alias to be created, and also the capable entity
  success, data = sandbox.scaf_call("cyberdyne/skynet/defense/nuke/launch")
  assert success
  alias = sandbox.ensure_aliased("cyberdyne/skynet/defense/nuke/launch")
  assert alias.name == "cyberdyne.skynet.defense.nuke.launch"

  assert sandbox.exists("cyberdyne/skynet/defense/nuke/entity.py"), "Expected action to exist after scaf call"


def test_relative_action_path_does_not_escape_cwd(sandbox: Sandbox):
  # Create a fake home directory and initialize it
  home = sandbox.chdir("home/mbd53")
  assert sandbox.scaf_init(), "Expected scaf_init to succeed in home directory"
  assert not sandbox.get_aliases(home), "Expected no aliases defined in home directory"

  # Create a nested project directory and chdir into it
  project = sandbox.chdir(home / "cyberdyne/skynet")
  assert project == home / "cyberdyne/skynet", f"Expected project to be in {home}"

  rel_action_path = "defense/nuke/launch"
  success, data = sandbox.scaf_call(rel_action_path)
  assert not success, "Expected relative action to fail due to lack of a reachable scaf deck"

  assert Path.cwd().name == project.name, "Expected to be in project directory"
  assert sandbox.scaf_init(), "Expected scaf init to succeed in project directory"
  project_aliases = sandbox.get_aliases(project)
  assert not project_aliases, "Expected no aliases defined in project directory after init"

  # Try calling the relative action again; this should create the alias in the project directory, not the home directory
  success, data = sandbox.scaf_call(rel_action_path)
  assert success, "Expected relative action call to succeed after scaf init in project directory"
  alias = sandbox.ensure_aliased(rel_action_path, project)
  assert alias.name == "defense.nuke.launch"
