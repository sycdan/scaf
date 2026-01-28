import os
from pathlib import Path

from jinja2 import Template
from scaf.user.create_action.command import CreateAction

from scaf import config
from scaf.alias.entity import Alias
from scaf.core.get_aliases.query import GetAliases
from scaf.tools import to_camel_case, to_dot_path

ACTION_DIR = Path(__file__).parent
TEMPLATES_DIR = ACTION_DIR / "templates"


# WIP
# def ensure_proto_files(proto_dir: Path):
#   contracts_file = proto_dir / "contracts.proto"
#   contracts_file.parent.mkdir(parents=True, exist_ok=True)
#   if contracts_file.exists():
#     raise RuntimeError(f"Proto file already exists: {contracts_file.relative_to(config.ROOT_DIR)}")

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


def ensure_logic_module(action_dir: Path, action_method: str):
  """will create handler.py in action_dir if it doesn't exist yet"""
  handler_file, created = _ensure_file_in(action_dir, "handler.py")
  if not created:
    return

  tpl_path = TEMPLATES_DIR / "handler.py.j2"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  content = tpl.render(
    action_method=action_method,
    action_method_capitalize=action_method.capitalize(),
    action_package=to_dot_path(handler_file.relative_to(config.ROOT_DIR)),
    action_camel=to_camel_case(action_dir.name),
    action_dot_path=to_dot_path(action_dir.relative_to(config.ROOT_DIR)),
  )
  handler_file.write_text(content)


def ensure_shape_module(action_dir: Path, action_method: str):
  """will create command.py (or query.py) in action_dir if it doesn't exist yet"""
  filename = "command.py" if action_method == "command" else "query.py"
  shape_file, created = _ensure_file_in(action_dir, filename)
  if not created:
    return

  tpl_path = TEMPLATES_DIR / "command.py.j2"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  content = tpl.render(
    action_camel=to_camel_case(action_dir.name),
    action_method_capitalize=action_method.capitalize(),
  )
  shape_file.write_text(content)


def handle(command: CreateAction) -> Alias:
  config.set_root_dir(os.getcwd())
  action_dir = config.ROOT_DIR / command.action_path
  action_dir.mkdir(parents=True, exist_ok=True)

  # Ensure all parents up to ROOT_DIR are packages
  curr = action_dir
  while curr != config.ROOT_DIR:
    _ensure_file_in(curr, "__init__.py")
    curr = curr.parent

  ensure_shape_module(action_dir, command.action_method)
  ensure_logic_module(action_dir, command.action_method)

  aliases = GetAliases(config.ROOT_DIR, filter=command.action_path.as_posix()).execute()
  if not aliases:
    raise RuntimeError(f"No alias found for created action at {command.action_path.as_posix()}")
  print("Reactivate your venv to pick up the new alias.")
  return aliases[0]
