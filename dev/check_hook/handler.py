import hashlib
from pathlib import Path

from check_hook.query import CheckHook


def get_file_hash(file_path: Path) -> str:
  """Get SHA256 hash of a file."""
  if not file_path.exists():
    return ""
  with open(file_path, "rb") as f:
    return hashlib.sha256(f.read()).hexdigest()


def handle(query: CheckHook) -> bool:
  """Check if installed pre-push hook matches source.

  Returns True if hooks match, False otherwise.
  """
  source_hook = Path("hooks/pre-push")
  installed_hook = Path(".git/hooks/pre-push")

  if not source_hook.exists():
    print("❌ Source hook not found: hooks/pre-push")
    return False

  if not installed_hook.exists():
    print("❌ Git hook not installed: .git/hooks/pre-push")
    print("💡 Run: cp hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push")
    return False

  source_hash = get_file_hash(source_hook)
  installed_hash = get_file_hash(installed_hook)

  if source_hash != installed_hash:
    print("❌ Installed git hook does not match source version")
    print(
      "💡 Reinstall hook: cp hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push"
    )
    return False

  print("✅ Git hook is up to date")
  return True
