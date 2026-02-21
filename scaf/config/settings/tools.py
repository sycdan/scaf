import logging
from pathlib import Path

from scaf.action_package.load.handler import _load_module_from_file

logger = logging.getLogger(__name__)


def get_settings_class(root: Path, domain: Path) -> type | None:
  settings_module_file = root / domain / "settings.py"
  if settings_module_file.exists():
    logger.debug(f"Loading {settings_module_file=}")
    module = _load_module_from_file(settings_module_file)
  else:
    logger.warning("No settings module found for domain '%s'", domain)
    return None

  try:
    cls = module.Settings
  except AttributeError:
    logger.warning(f"No Settings class found in {module.__file__}")
    return None
  if not isinstance(cls, type):
    logger.warning(f"Settings in {module.__file__} is not a class")
    return None
  if not hasattr(cls, "__dataclass_fields__"):
    logger.warning(f"Settings class in {module.__file__} is not a dataclass")
    return None
  return cls
