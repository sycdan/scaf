import hashlib
import logging
from pathlib import Path

from dev.check.is_git_hook_updated.query import IsGitHookUpdated
from scaf import config

logger = logging.getLogger(__name__)


def get_file_hash(file_path: Path) -> str:
  if not file_path.exists():
    return ""
  with file_path.open("rb") as f:
    return hashlib.sha256(f.read()).hexdigest()


def handle(query: IsGitHookUpdated) -> bool:
  """returns true if the installed git hook matches the source version."""

  installed_hook = query.hook_file
  hook_name = installed_hook.name
  source_hook = Path(config.REPO_ROOT) / "hooks" / hook_name

  if not installed_hook.exists():
    logger.warning("Hook not installed: %s", installed_hook)
    return False

  if not source_hook.exists():
    logger.warning("Hook source not found: %s", source_hook)
    return False

  installed_hash = get_file_hash(installed_hook)
  source_hash = get_file_hash(source_hook)

  if installed_hash != source_hash:
    logger.warning("Installed %s hook does not match source version", hook_name)
    return False

  logger.info("Git %s hook is up to date", hook_name)
  return True
