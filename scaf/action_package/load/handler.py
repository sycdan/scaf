import importlib.util
import logging
from pathlib import Path
from types import ModuleType

from scaf.action_package.entity import ActionPackage
from scaf.action_package.load.command import LoadActionPackage
from scaf.action_package.rules import must_contain_required_files
from scaf.tools import compute_hash

logger = logging.getLogger(__name__)


def _load_module_from_file(file: Path, hash: str = "") -> ModuleType:
  if file.is_dir():
    file = file / "__init__.py"

  if not file.exists():
    raise RuntimeError(f"Module file does not exist: {file}")

  hash = hash or compute_hash(file)
  module_name = f"module_{hash}"
  spec = importlib.util.spec_from_file_location(module_name, str(file))
  if not spec or not spec.loader:
    raise RuntimeError(f"Could not load module from {file}")

  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def ensure_action_folder(action_path: Path) -> Path:
  """in case we got a path to a file inside the action package"""
  if not action_path.exists():
    raise ActionPackage.DoesNotExist(action_path.as_posix())

  action_folder = action_path if action_path.is_dir() else action_path.parent
  return action_folder


def load_init_module(action_folder: Path) -> ModuleType:
  return _load_module_from_file(action_folder / "__init__.py")


def load_shape_module(action_folder: Path) -> ModuleType:
  try:
    return _load_module_from_file(action_folder / "command.py")
  except RuntimeError as e:
    logger.debug(str(e))
    try:
      return _load_module_from_file(action_folder / "query.py")
    except RuntimeError:
      logger.debug(str(e))
      raise RuntimeError(f"Failed to load action shape module from {action_folder.as_posix()}")


def load_logic_module(action_dir: Path) -> ModuleType:
  return _load_module_from_file(action_dir / "handler.py")


def handle(command: LoadActionPackage) -> ActionPackage:
  logger.debug(f"Handling {command=}")
  action_folder = ensure_action_folder(command.root / command.action)
  must_contain_required_files([f.name for f in action_folder.iterdir()])
  init_module = load_init_module(action_folder)
  shape_module = load_shape_module(action_folder)
  logic_module = load_logic_module(action_folder)
  logger.info(f"Action package loaded from {action_folder.as_posix()}")
  return ActionPackage(
    action_folder=action_folder,
    init_module=init_module,
    shape_module=shape_module,
    logic_module=logic_module,
  )
