import logging
import sys
from pathlib import Path

from scaf.action_package.load.command import LoadActionPackage
from scaf.alias.entity import Alias
from scaf.alias.tools import parse_all_aliases
from scaf.config import SCAF_FOLDER_NAME
from scaf.deck.locate.command import LocateDeck
from scaf.output import NC, RED
from scaf.user.call.handler import ensure_import_path
from scaf.user.show.query import Show

logger = logging.getLogger(__name__)


def _get_docstring(alias: Alias, root: Path) -> str:
  """Load the action package for an alias and return the shape docstring."""
  try:
    ap = LoadActionPackage(root=root, action=alias.action).execute()
    doc = (ap.shape_class.__doc__ or ap.shape_module.__doc__ or "").strip().splitlines()[0]
    return doc
  except Exception:
    return ""


def _print_alias_listing(aliases: list[Alias], root: Path) -> None:
  """Print each alias name in red followed by its docstring to stderr."""
  for alias in aliases:
    doc = _get_docstring(alias, root)
    raw_cmd = alias.to_bash()
    logger.info("  %s", raw_cmd)
    print(f"{RED}{alias.name}{NC}  {doc}", file=sys.stderr)


def handle(query: Show):
  # LocateDeck searches the start path's parents, so point it at cwd/.scaf to include cwd itself.
  deck = LocateDeck(path=Path.cwd().resolve() / SCAF_FOLDER_NAME).execute()
  ensure_import_path(deck)

  # Read-only: parse and list the existing aliases without writing back (unlike discover).
  aliases = parse_all_aliases(deck.aliases_file, deck.root)
  _print_alias_listing(aliases, deck.root)
