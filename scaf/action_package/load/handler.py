import importlib.util
from pathlib import Path
from types import ModuleType

from scaf import config
from scaf.action_package.entity import ActionPackage
from scaf.action_package.load.query import LoadActionPackage
from scaf.action_package.rules import must_contain_required_files
from scaf.output import print_warning
from scaf.tools import compute_hash, resolve_path


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


def ensure_action_dir(action_path: Path | str) -> Path:
  action_path = resolve_path(action_path)

  if not action_path.is_relative_to(config.ROOT_DIR):
    raise RuntimeError(f"Action path is not relative to root: {action_path.as_posix()}")

  if not action_path.exists():
    raise RuntimeError(f"Action path does not exist: {action_path.as_posix()}")

  action_dir = action_path if action_path.is_dir() else action_path.parent
  return action_dir


def load_init_module(action_dir: Path) -> ModuleType:
  return _load_module_from_file(action_dir / "__init__.py")


def load_shape_module(action_dir: Path) -> ModuleType:
  try:
    return _load_module_from_file(action_dir / "command.py")
  except RuntimeError as e:
    if config.DEBUG:
      print_warning(str(e))
    try:
      return _load_module_from_file(action_dir / "query.py")
    except RuntimeError:
      if config.DEBUG:
        print_warning(str(e))
      raise RuntimeError(f"Failed to load action shape module from {action_dir.as_posix()}")


def load_logic_module(action_dir: Path) -> ModuleType:
  return _load_module_from_file(action_dir / "handler.py")


def handle(query: LoadActionPackage) -> ActionPackage:
  action_dir = ensure_action_dir(query.action_path)
  must_contain_required_files([f.name for f in action_dir.iterdir()])
  init_module = load_init_module(action_dir)
  shape_module = load_shape_module(action_dir)
  logic_module = load_logic_module(action_dir)
  return ActionPackage(
    action_dir=action_dir,
    init_module=init_module,
    shape_module=shape_module,
    logic_module=logic_module,
  )
