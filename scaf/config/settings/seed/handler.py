import logging
from pathlib import Path

from scaf.config.settings.seed.command import SeedSettings

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "settings.py.tmpl"


def handle(command: SeedSettings) -> None:
  logger.debug(f"Handling {command=}")

  command.domain_path.mkdir(parents=True, exist_ok=True)
  settings_path = command.domain_path / "settings.py"

  template = _TEMPLATE_PATH.read_text()
  content = template + f"\n  {command.setting}: str = {repr(command.value)}\n"
  settings_path.write_text(content)
  logger.info(f"Created {settings_path} with field '{command.setting}'")
