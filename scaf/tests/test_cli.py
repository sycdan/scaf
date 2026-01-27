from pathlib import Path

import pytest

from scaf import cli

domain_root = Path("example")


def test_action_alias_are_deduplicated():
  work_folder = Path("tld")

  action_paths = [
    "my/service/remote/deploy",
    "my/server/remote/deploy",
  ]

  aliases = cli.generate_action_aliases(work_folder, action_paths)

  # Verify the deduplication worked correctly
  aliases_text = "\n".join(aliases)
  assert "tld.deploy-remote-service" in aliases_text
  assert "tld.deploy-remote-server" in aliases_text


@pytest.mark.integration
def test_call_invalid_path_shows_error(capsys):
  with pytest.raises(SystemExit) as excinfo:
    cli.main(["non_existent_action"])

  assert excinfo.value.code != 0

  captured = capsys.readouterr()
  assert "does not exist:" in captured.err


@pytest.mark.integration
def test_call_invalid_work_folder_shows_error(capsys):
  invalid_action_folder = domain_root / "not_an_action"

  cli.main([invalid_action_folder.as_posix()])

  captured = capsys.readouterr()
  assert "No action packages found in:" in captured.err


@pytest.mark.integration
def test_domain_folder_generates_aliases(capsys):
  """Test that calling CLI with a domain folder generates bash aliases."""
  cli.main([domain_root.as_posix()])

  captured = capsys.readouterr()
  output_lines = captured.out.strip().split("\n")

  # Should generate aliases for the action packages in example domain
  aliases = [line for line in output_lines if line.startswith("alias ")]

  # Verify we have at least one alias
  assert len(aliases) > 0

  # Check that aliases follow the expected format
  for alias in aliases:
    assert alias.startswith("alias example.")
    assert "=" in alias
    assert "scaf " in alias

  # Should find the insert_peg action
  insert_peg_alias = [a for a in aliases if "insert-peg" in a]
  assert len(insert_peg_alias) == 1
  assert "example.insert-peg=" in insert_peg_alias[0]
