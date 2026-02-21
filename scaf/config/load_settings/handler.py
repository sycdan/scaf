import logging
from dataclasses import fields, replace
from pathlib import Path
from types import ModuleType

from scaf.action_package.load.handler import _load_module_from_file
from scaf.config.load_settings.query import LoadSettings
from scaf.deck.entity import Deck
from scaf.deck.locate.command import LocateDeck
from scaf.tools import read_json_file

logger = logging.getLogger(__name__)


def _load_settings_module(deck: Deck, domain: Path) -> ModuleType:
  settings_module_file = deck.root / domain / "settings.py"
  if settings_module_file.exists():
    logger.debug("Loading domain settings: %s", settings_module_file)
    return _load_module_from_file(settings_module_file)
  raise ValueError(f"No settings.py found for domain '{domain}'")


def handle(query: LoadSettings):
  logger.debug(f"Handling {query=}")

  domain = Path(query.domain).expanduser()
  if not domain.is_absolute():
    domain = Path.cwd() / domain

  deck = LocateDeck(path=domain).execute()
  if deck is None:
    raise RuntimeError("No scaf deck found. Run 'scaf init' first.")

  domain_rel = domain.relative_to(deck.root)
  module = _load_settings_module(deck, domain_rel)
  cls = module.Settings
  defaults = cls()

  data = read_json_file(deck.settings_file)
  node = data
  for part in domain_rel.parts:
    node = node.get(part, {})

  known = {f.name for f in fields(cls)}
  overrides = {k: v for k, v in node.items() if k in known}

  return replace(defaults, **overrides)
