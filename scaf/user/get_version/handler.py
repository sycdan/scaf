import re
from pathlib import Path
from scaf.user.get_version.query import GetVersionQuery


def handle(query: GetVersionQuery) -> str:
  """Get the current version from scaf/__init__.py.

  Returns the version string.
  """
  init_file = Path("scaf/__init__.py")

  if not init_file.exists():
    raise FileNotFoundError("scaf/__init__.py not found")

  with open(init_file, "r") as f:
    content = f.read()

  version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)

  if not version_match:
    raise ValueError("Could not find __version__ in scaf/__init__.py")

  return version_match.group(1)
