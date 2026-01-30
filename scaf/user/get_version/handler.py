import re

from scaf import config
from scaf.user.get_version.query import GetVersionQuery


def handle(query: GetVersionQuery) -> str:
  init_file = config.REPO_ROOT / "scaf/__init__.py"

  if not init_file.exists():
    raise FileNotFoundError(f"{init_file} not found")

  with open(init_file, "r") as f:
    content = f.read()

  version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)

  if not version_match:
    raise ValueError(f"Could not find __version__ in {init_file}")

  return version_match.group(1)
