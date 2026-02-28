import sys
import uuid

from test.integration.conftest import Sandbox


def test_discover_writes_aliases_to_file(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init(0)  # Init with no discovery so aliases file has no actions yet

  success, stdout, stderr = sandbox.scaf("discover", ".")

  assert success, f"Expected discover to succeed\nstdout={stdout}\nstderr={stderr}"

  # Aliases for all example actions should now be in the aliases file
  for expected_action, expected_name in [
    ("example/custom_union_types", "example.custom-union-types"),
    ("example/hole/insert_peg", "example.hole.insert-peg"),
    ("example/myriad/get", "example.myriad.get"),
    ("example/pass_dynamic_args", "example.pass-dynamic-args"),
    ("example/test_timestamp_handling", "example.test-timestamp-handling"),
  ]:
    alias = sandbox.ensure_aliased(expected_action)
    assert alias.name == expected_name


def test_discover_preserves_manually_renamed_alias(sandbox: Sandbox):
  """Discover must not overwrite a manually chosen alias name with the default one."""
  from pathlib import Path

  from scaf.alias.entity import Alias
  from scaf.config import ALIASES_FILENAME, SCAF_FOLDER_NAME

  sandbox.scaf_init(0)  # Create aliases file with no action aliases
  sandbox.add_example_domain()

  # Manually write a custom-named alias for a known action
  custom_name = f"x{uuid.uuid4().hex[:8]}"  # Unique name to avoid collisions
  action_path = "example/myriad/get"
  custom_alias = Alias(name=custom_name, action=Path(action_path), root=sandbox.root)
  aliases_file = sandbox.root / SCAF_FOLDER_NAME / ALIASES_FILENAME
  aliases_file.write_text(
    aliases_file.read_text(encoding="utf-8").rstrip("\n") + "\n" + custom_alias.to_bash() + "\n",
    encoding="utf-8",
  )

  # Confirm our custom alias is present before discovery
  found = sandbox.ensure_aliased(action_path)
  assert found.name == custom_name, (
    f"Setup failed: expected name '{custom_name}', got '{found.name}'"
  )

  # Run discover
  success, stdout, stderr = sandbox.scaf("discover", ".")
  assert success, f"Expected discover to succeed\nstdout={stdout}\nstderr={stderr}"

  # The custom name must be preserved — not replaced by the default 'example.myriad.get'
  after = sandbox.ensure_aliased(action_path)
  assert after.name == custom_name, (
    f"Discover overwrote manual alias '{custom_name}' with '{after.name}'"
  )

  # The default-named alias must NOT have been added as a duplicate
  all_names = {a.name for a in sandbox.get_aliases()}
  default_name = "example.myriad.get"
  assert default_name not in all_names, (
    f"Discover added default alias '{default_name}' despite '{custom_name}' already existing"
  )


def test_discover_prints_alias_names_in_red(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init(0)

  success, stdout, stderr = sandbox.scaf("discover", ".")
  assert success

  RED = "\033[0;31m"
  # All discovered alias names should appear in red in stderr
  for _, expected_name in [
    ("example/custom_union_types", "example.custom-union-types"),
    ("example/hole/insert_peg", "example.hole.insert-peg"),
    ("example/myriad/get", "example.myriad.get"),
  ]:
    assert RED + expected_name in stderr, (
      f"Expected '{expected_name}' to appear in red in stderr\nstderr={stderr}"
    )


def test_discover_info_logs_raw_command_for_each_alias(sandbox: Sandbox):
  sandbox.add_example_domain()
  sandbox.scaf_init(0)

  # Run via subprocess with verbosity=2 so a fresh logging config captures info logs
  # Use sys.executable -m scaf to ensure the current env's scaf is used, not a system-installed one
  result = sandbox.run(sys.executable, "-m", "scaf", "--verbose", "--verbose", "discover", ".")

  assert result.returncode == 0, (
    f"Expected discover to succeed\nstdout={result.stdout}\nstderr={result.stderr}"
  )
  # The raw scaf call command should appear in the logs for at least one alias
  assert "scaf call $DECK/" in result.stderr, (
    f"Expected info log with raw scaf call command\nstderr={result.stderr}"
  )
