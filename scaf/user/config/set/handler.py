import logging
from dataclasses import fields
from pathlib import Path

from scaf.config.settings.seed.command import SeedSettings
from scaf.config.settings.tools import get_settings_class
from scaf.deck.locate.command import LocateDeck
from scaf.output import print_success
from scaf.tools import get_fitter, read_json_file, write_json_file
from scaf.user.config.set.command import SetConfig

logger = logging.getLogger(__name__)


def handle(command: SetConfig):
  logger.debug(f"Handling {command=}")

  domain = command.domain.expanduser()
  if not domain.is_absolute():
    domain = Path.cwd() / domain

  deck = LocateDeck(path=domain).execute()
  domain_rel = domain.relative_to(deck.root)

  cls = get_settings_class(deck.root, domain_rel)
  if not cls:
    SeedSettings(
      domain_path=deck.root / domain_rel, setting=command.setting, value=command.value
    ).execute()
    data = read_json_file(deck.settings_file)
    node = data
    for part in domain_rel.parts:
      node = node.setdefault(part, {})
    node[command.setting] = command.value
    write_json_file(deck.settings_file, data)
    print_success(
      f"Created settings for {domain_rel} and set {command.setting} = {command.value!r}"
    )
    return

  known = {f.name: f for f in fields(cls)}
  if command.setting not in known:
    raise RuntimeError(
      f"'{command.setting}' is not a valid setting for '{domain_rel}'. "
      f"Known settings: {', '.join(sorted(known))}"
    )

  fitter = get_fitter(cls, command.setting)
  try:
    coerced = fitter(command.value)
  except (ValueError, TypeError) as e:
    raise RuntimeError(f"Invalid value {command.value!r} for '{command.setting}': {e}") from e

  data = read_json_file(deck.settings_file)
  node = data
  for part in domain_rel.parts:
    node = node.setdefault(part, {})
  node[command.setting] = coerced

  write_json_file(deck.settings_file, data)
  print_success(f"Set {domain_rel}/{command.setting} = {coerced!r}")
