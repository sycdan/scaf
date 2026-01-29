import subprocess

import pytest

from test.alias.entity import Alias


@pytest.mark.integration
@pytest.mark.parametrize(
  "root,expected_aliases",
  [
    (".", ["dev.bump-version"]),
    ("", ["scaf.create-action"]),
  ],
)
def test_expected_aliases_are_exposed(root, expected_aliases):
  found = {k: False for k in expected_aliases}
  result = subprocess.run(["scaf", root], capture_output=True, text=True)
  raw_aliases = result.stdout.splitlines()
  aliases = [Alias.from_raw(alias) for alias in raw_aliases if alias.strip()]
  for alias in aliases:
    found[alias.name] = True
  assert not any(v is False for v in found.values())
