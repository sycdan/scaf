"""
Bug ID: 202601270041
Issue: CLI argument mapping generates underscore flags instead of slug-case flags

The client expects --force-insert but CLI was generating --force_insert.
This breaks the user experience as standard CLI tools use slug-case.
"""

from pathlib import Path

import pytest

from scaf import cli

domain_root = Path("example")


@pytest.mark.integration
def test_insert_peg_with_slug_case_flags():
  """Test that CLI accepts slug-case flags for underscore field names."""
  insert_peg_action = domain_root / "hole" / "insert_peg"

  # This should work with slug-case flags
  try:
    cli.main([insert_peg_action.as_posix(), "square", "square", "--force-insert"])
  except Exception as e:
    pytest.fail(f"CLI should accept slug-case flags, but got error: {e}")


@pytest.mark.integration
def test_insert_peg_shows_slug_case_in_help(capsys):
  """Test that help output shows slug-case flags."""
  insert_peg_action = domain_root / "hole" / "insert_peg"

  cli.main([insert_peg_action.as_posix(), "--help"])
  captured = capsys.readouterr()

  # Verify help shows slug-case flags
  assert "--force-insert" in captured.out
  # Make sure it doesn't show underscore versions
  assert "--force_insert" not in captured.out
