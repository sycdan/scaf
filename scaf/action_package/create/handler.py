import logging
from pathlib import Path

from jinja2 import Template

from scaf.action_package.create.command import CreateActionPackage
from scaf.action_package.entity import ActionPackage
from scaf.action_package.load.command import LoadActionPackage
from scaf.alias.entity import Alias
from scaf.deck.entity import Deck
from scaf.tools import to_camel_case, to_dot_path

ACTION_DIR = Path(__file__).parent
TEMPLATES_DIR = ACTION_DIR / "templates"

logger = logging.getLogger(__name__)


# WIP
# def ensure_proto_files(proto_dir: Path):
#   contracts_file = proto_dir / "contracts.proto"
#   contracts_file.parent.mkdir(parents=True, exist_ok=True)
#   if contracts_file.exists():
#     raise RuntimeError(f"Proto file already exists: {contracts_file.relative_to(config.REPO_ROOT)}")

#   tmpl_path = TEMPLATES_DIR / "contracts.proto.tmpl"
#   tmpl = Template(tmpl_path.read_text(encoding="utf-8"))
#   package_path = proto_dir.relative_to(config.PROTO_DIR)
#   proto_content = tmpl.substitute(
#     action_package=to_dot_path(package_path),
#     action_camel=to_camel_case(package_path.name),
#   )
#   contracts_file.write_text(proto_content.strip() + "\n")
#   return [
#     contracts_file,
#   ]


def _create_empty_file(file_path: Path):
  """Example:
  ```
  if _create_empty_file(some_path):
    print("created new file")
  else:
    print("file already existed")
  ```
  """
  if not file_path.exists():
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("")
    return True
  return False


def _ensure_file_in(action_dir: Path, filename: str) -> tuple[Path, bool]:
  file_path = action_dir / filename
  if _create_empty_file(file_path):
    return file_path, True
  return file_path, False


def ensure_traversable_package(root: Path, action: Path):
  action_folder = root / action
  action_folder.mkdir(parents=True, exist_ok=True)

  curr = action_folder
  while curr != root:
    _ensure_file_in(curr, "__init__.py")
    curr = curr.parent

  return action_folder


def ensure_logic_module(action_folder: Path, action_method: str, root: Path):
  """will create handler.py in action_dir if it doesn't exist yet"""
  logic_file, created = _ensure_file_in(action_folder, "handler.py")
  if not created:
    return

  tpl_path = TEMPLATES_DIR / "handler.py.j2"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  content = tpl.render(
    action_method=action_method,
    action_method_capitalize=action_method.capitalize(),
    action_package=to_dot_path(logic_file.relative_to(root)),
    action_camel=to_camel_case(action_folder.name),
    action_dot_path=to_dot_path(action_folder.relative_to(root)),
  )
  logic_file.write_text(content)


def ensure_shape_module(action_folder: Path, action_method: str):
  """will create command.py (or query.py) in action_dir if it doesn't exist yet"""
  filename = "command.py" if action_method == "command" else "query.py"
  shape_file, created = _ensure_file_in(action_folder, filename)
  if not created:
    return

  tpl_path = TEMPLATES_DIR / f"{action_method}.py.j2"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  content = tpl.render(
    action_camel=to_camel_case(action_folder.name),
    action_method_capitalize=action_method.capitalize(),
  )
  shape_file.write_text(content)


def add_alias(action_folder: Path, deck: Deck):
  alias_file = deck.aliases_file
  if not alias_file.exists():
    logger.warning(f"{alias_file} not found. Skipping alias creation.")
    return

  root = deck.root
  action = action_folder.relative_to(root)

  alias = Alias(
    name=to_dot_path(action),
    root=root,
    action=action,
  )

  with alias_file.open("a", encoding="utf-8") as f:
    f.write(f"{alias.to_bash()}\n")


def handle(command: CreateActionPackage) -> ActionPackage:
  deck = command.deck
  root = deck.root
  action_method = command.method
  action_folder = ensure_traversable_package(root, command.action)
  ensure_shape_module(action_folder, action_method)
  ensure_logic_module(action_folder, action_method, root)
  add_alias(action_folder, deck)
  return LoadActionPackage(root=root, action=action_folder.relative_to(root)).execute()
