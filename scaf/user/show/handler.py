from pathlib import Path

from scaf.alias.tools import parse_all_aliases
from scaf.config import SCAF_FOLDER_NAME
from scaf.deck.locate.command import LocateDeck
from scaf.user.call.handler import ensure_import_path
from scaf.user.discover.handler import _print_alias_listing
from scaf.user.show.query import Show


def handle(query: Show):
  # LocateDeck searches the start path's parents, so point it at cwd/.scaf to include cwd itself.
  deck = LocateDeck(path=Path.cwd().resolve() / SCAF_FOLDER_NAME).execute()
  ensure_import_path(deck)

  # Read-only: parse and list the existing aliases without writing back (unlike discover).
  aliases = parse_all_aliases(deck.aliases_file, deck.root)
  _print_alias_listing(aliases, deck.root)
