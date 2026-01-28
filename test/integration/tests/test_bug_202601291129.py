"""Bug test: capability should only be added to alias when necessary for deduplication."""

import subprocess

import pytest

from test.alias.entity import Alias


@pytest.mark.integration
def test_capability_only_added_when_necessary_for_deduplication():
  """
  Bug: scaf actions like 'scaf/user/create_action' currently generate
  aliases like 'scaf.user.create-action' but should generate
  'scaf.create-action' unless there's a conflict requiring deduplication.
  """
  # Test the scaf root which contains scaf/user/create_action and scaf/user/get_version
  result = subprocess.run(["scaf", ""], capture_output=True, text=True)
  raw_aliases = result.stdout.splitlines()
  aliases = [Alias.from_raw(alias) for alias in raw_aliases if alias.strip()]

  # Find the aliases we care about
  alias_names = [alias.name for alias in aliases]

  # Both actions should NOT have capability prefix since there are no conflicts
  assert "scaf.create-action" in alias_names, (
    f"Expected 'scaf.create-action' but got: {alias_names}"
  )
  assert "scaf.get-version" in alias_names, f"Expected 'scaf.get-version' but got: {alias_names}"

  # The buggy behavior (these should NOT be present)
  assert "scaf.user.create-action" not in alias_names, (
    f"Should not have capability prefix: {alias_names}"
  )
  assert "scaf.user.get-version" not in alias_names, (
    f"Should not have capability prefix: {alias_names}"
  )
