import argparse
import dataclasses
import os
import typing
from pathlib import Path
from pprint import pprint
from typing import get_args, get_origin

from scaf import config
from scaf.action_package.load.query import LoadActionPackage
from scaf.core.rules import ensure_absolute_path, is_action_package
from scaf.output import print_error
from scaf.tools import find_available_actions, to_slug_case


def get_scaf_package_path() -> Path:
  """Get the path to the installed scaf package."""
  import scaf

  scaf_module_path = Path(scaf.__file__).parent
  return scaf_module_path


def resolve_work_folder_path(work_folder_arg: str) -> Path:
  """Resolve work folder argument, handling special cases for scaf's own actions."""

  # Find scaf's own actions
  if not work_folder_arg:
    return get_scaf_package_path()

  return ensure_absolute_path(work_folder_arg)


def handle_action_package(folder: Path, action_args: list, show_help: bool = False):
  domain_action = LoadActionPackage(folder).execute()
  description = domain_action.init_module.__doc__ or "No comment."

  shape_class = domain_action.shape_class
  action_parser = build_parser_from_shape(shape_class, description=description)
  action_parser.prog = f"scaf {domain_action.action_dir.relative_to(config.ROOT_DIR).as_posix()}"

  # Show action-specific help if requested
  if show_help:
    action_parser.print_help()
    return

  try:
    args = action_parser.parse_args(action_args)
  except SystemExit:  # argparse throws SystemExit on parse errors
    raise RuntimeError("Invalid action arguments.")
  action = shape_class(**vars(args))
  pprint(domain_action.logic_module.handle(action))


def normalize_argparse_type(t):
  origin = get_origin(t)

  # Optional[T] or Union[T, None]
  if origin is typing.Union:
    args = [a for a in get_args(t) if a is not type(None)]
    if len(args) == 1:
      return normalize_argparse_type(args[0])
    # fallback: treat as string
    return str

  # bare type
  return t


def build_parser_from_shape(shape_class: type, description: str):
  parser = argparse.ArgumentParser(description=description)

  for field in dataclasses.fields(shape_class):
    name = field.name
    type_ = normalize_argparse_type(field.type)
    default = field.default

    if default is dataclasses.MISSING:
      # required positional
      parser.add_argument(name, type=type_)
    else:
      flag_name = to_slug_case(name)
      if type_ is bool:
        parser.add_argument(f"--{flag_name}", action="store_true", default=default, dest=name)
      else:
        parser.add_argument(f"--{flag_name}", type=type_, default=default, dest=name)

  return parser


def generate_action_aliases(work_folder: Path, action_paths: list[str]) -> list[str]:
  """Generate bash aliases for action packages with deduplication."""
  work_folder_name = work_folder.name
  aliases = []

  # Create initial alias mappings
  alias_map = {}
  for action_path in action_paths:
    path_parts = action_path.split("/")
    action_name = to_slug_case(path_parts[-1])
    base_alias = f"{work_folder_name}.{action_name}"

    if base_alias not in alias_map:
      alias_map[base_alias] = [action_path]
    else:
      alias_map[base_alias].append(action_path)

  # Handle deduplication
  final_aliases = {}
  for base_alias, paths in alias_map.items():
    if len(paths) == 1:
      # No conflict, use base alias
      action_path = paths[0]
      scaf_command = f"scaf {(work_folder / action_path).as_posix()}"
      final_aliases[base_alias] = scaf_command
    else:
      # Conflict, need to deduplicate by adding parent folders
      # Find minimum depth needed to make all paths unique
      max_depth = min(
        len(path.split("/")) - 1 for path in paths
      )  # -1 because we exclude the action name

      for depth in range(1, max_depth + 1):
        candidates = {}
        all_unique = True

        for action_path in paths:
          path_parts = action_path.split("/")
          action_name = to_slug_case(path_parts[-1])

          # Build parent suffix using the specified depth
          parent_parts = []
          for i in range(depth):
            if len(path_parts) >= 2 + i:  # Ensure we have enough parts
              parent_parts.append(path_parts[-(2 + i)].replace("_", "-"))

          parent_suffix = "-".join(parent_parts) if parent_parts else ""
          candidate_alias = f"{work_folder_name}.{action_name}-{parent_suffix}"

          if candidate_alias in candidates:
            all_unique = False
            break
          candidates[candidate_alias] = action_path

        if all_unique:
          # Found a depth that makes all aliases unique
          for alias_name, action_path in candidates.items():
            scaf_command = f"scaf {(work_folder / action_path).as_posix()}"
            final_aliases[alias_name] = scaf_command
          break

  # Generate bash alias statements
  for alias_name, command in sorted(final_aliases.items()):
    aliases.append(f"alias {alias_name}='{command}'")

  return aliases


def handle_domain_capability(work_folder: Path):
  """Handle a domain/capability folder by finding all action packages and generating aliases."""
  action_paths = find_available_actions(work_folder)

  if not action_paths:
    print_error(f"No action packages found in: {work_folder.as_posix()}")
    return

  aliases = generate_action_aliases(work_folder, action_paths)
  for alias in aliases:
    print(alias)


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Discover or execute a domain action.",
    add_help=False,  # We'll handle help manually
    prog="scaf",
  )
  parser.add_argument(
    "work_folder",
    nargs="?",
    default="",
    help="Path to a domain directory. Use '--self' to load scaf's own actions.",
  )
  parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
  args, remaining = parser.parse_known_args(argv)

  # Show base help if no work_folder is provided
  if not args.work_folder and args.help:
    parser.print_help()
    return

  config.set_root_dir(os.getcwd())

  try:
    work_folder = resolve_work_folder_path(args.work_folder)
    if not work_folder.exists():
      raise RuntimeError(f"Work folder does not exist: {work_folder.as_posix()}")
    if is_action_package(work_folder):
      handle_action_package(work_folder, remaining, args.help)
    else:
      # Assume it's a domain/capability and look for action packages within
      handle_domain_capability(work_folder)
  except (ValueError, RuntimeError) as e:
    print_error(str(e))
    exit(1)
