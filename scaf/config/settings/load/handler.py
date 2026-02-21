import logging
from dataclasses import fields, replace
from pathlib import Path

from scaf.config.settings.load.query import LoadSettings
from scaf.config.settings.tools import get_settings_class
from scaf.deck.locate.command import LocateDeck
from scaf.tools import read_json_file

logger = logging.getLogger(__name__)


def handle(query: LoadSettings):
  logger.debug(f"Handling {query=}")

  domain = Path(query.domain).expanduser()
  if not domain.is_absolute():
    domain = Path.cwd() / domain

  deck = LocateDeck(path=domain).execute()
  domain_rel = domain.relative_to(deck.root)
  if not (cls := get_settings_class(deck.root, domain_rel)):
    return None
  defaults = cls()

  data = read_json_file(deck.settings_file)
  node = data
  for part in domain_rel.parts:
    node = node.get(part, {})

  known = {f.name for f in fields(cls)}
  overrides = {k: v for k, v in node.items() if k in known}

  return replace(defaults, **overrides)
