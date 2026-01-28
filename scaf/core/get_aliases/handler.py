"""Constructs bash aliases for action packages in a domain/capability."""

import os
from pathlib import Path

from scaf.action_package.rules import must_contain_required_files
from scaf.alias.entity import Alias
from scaf.core.get_aliases.query import GetAliases
from scaf.output import print_error
from scaf.tools import to_slug_case


def find_available_actions(domain_folder: Path) -> list[str]:
  actions = []
  for base, dirs, files in os.walk(domain_folder):
    # Skip hidden directories and __pycache__ etc.
    dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
    try:
      must_contain_required_files(files)
      actions.append(Path(base).relative_to(domain_folder).as_posix())
    except ValueError:
      continue
  return sorted(actions)


def generate_action_aliases(root: Path, action_paths: list[str]) -> list[Alias]:
  work_folder_name = root.name
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
      final_aliases[base_alias] = action_path
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
            final_aliases[alias_name] = action_path
          break

  for alias_name, action_path in sorted(final_aliases.items()):
    aliases.append(Alias(name=alias_name, root=root, action=Path(action_path)))

  return aliases


def handle_domain_capability(folder: Path):
  action_paths = find_available_actions(folder)

  if not action_paths:
    print_error(f"No action packages found in: {folder.as_posix()}")
    return

  aliases = generate_action_aliases(folder, action_paths)
  for alias in aliases:
    print(alias)


def handle(command: GetAliases) -> list[Alias]:
  actions = find_available_actions(command.root)
  aliases = generate_action_aliases(command.root, actions)
  if command.filter:
    aliases = [a for a in aliases if a.action.as_posix().startswith(command.filter)]
  return aliases
