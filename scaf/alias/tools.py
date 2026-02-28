import logging
from pathlib import Path

from scaf.alias.entity import Alias

logger = logging.getLogger(__name__)


def parse_all_aliases(aliases_file: Path, root: Path) -> list[Alias]:
  """Parse every alias line in the file, logging a warning for each invalid line."""
  parsed: list[Alias] = []
  if not aliases_file.exists():
    return parsed
  for raw in aliases_file.read_text(encoding="utf-8").splitlines():
    raw = raw.strip()
    if not raw:
      continue
    try:
      if raw.startswith("#") or raw[0].isupper() or raw.startswith("echo "):
        continue  # Skip comment lines and constants
      parsed.append(Alias.from_bash(raw, root=root))
    except ValueError as exc:
      logger.warning("Could not parse alias line: %r — %s", raw, exc)
  return parsed


def append_aliases(aliases_file: Path, new_aliases: list[Alias]) -> None:
  """Append new aliases to an existing aliases file.

  The file must already exist (created by ``scaf init`` via the template).
  Call sites are responsible for filtering out already-known action paths before calling this.
  """
  if not new_aliases:
    logger.info("No new aliases to add to %s", aliases_file)
    return
  new_lines = "\n".join(alias.to_bash() for alias in new_aliases)
  existing = aliases_file.read_text(encoding="utf-8")
  aliases_file.write_text(existing.rstrip("\n") + "\n" + new_lines + "\n", encoding="utf-8")
  logger.info("Added %d new alias(es) to %s", len(new_aliases), aliases_file)
