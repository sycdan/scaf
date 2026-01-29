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


def generate_verb_noun_name(action_name: str, capability: str) -> str:
  """Generate verb-noun pattern from action and capability names."""
  action_slug = to_slug_case(action_name)
  capability_slug = to_slug_case(capability)

  # If action contains underscore, it's already verb_noun -> verb-noun
  if "_" in action_name:
    return action_slug

  # Single verb + capability -> verb-capability
  return f"{action_slug}-{capability_slug}"


def generate_action_aliases(root: Path, action_paths: list[str]) -> list[Alias]:
  work_folder_name = root.name

  # Step 1: Generate preferred alias for each action
  action_data = []
  for action_path in action_paths:
    path_parts = action_path.split("/")
    action_name = path_parts[-1]

    if len(path_parts) == 1:
      # Root level action - use simple name
      preferred_alias = to_slug_case(action_name)
    elif len(path_parts) == 2:
      # capability/action pattern
      capability = path_parts[-2]
      preferred_alias = generate_verb_noun_name(action_name, capability)
    else:
      # domain/capability/action or deeper - use verb-noun with immediate parent
      capability = path_parts[-2]
      preferred_alias = generate_verb_noun_name(action_name, capability)

    action_data.append(
      {
        "path": action_path,
        "path_parts": path_parts,
        "preferred_alias": preferred_alias,
        "action_name": action_name,
      }
    )

  # Step 2: Detect conflicts and resolve with minimal path inclusion
  alias_map = {}
  for data in action_data:
    preferred = data["preferred_alias"]
    if preferred not in alias_map:
      alias_map[preferred] = []
    alias_map[preferred].append(data)

  # Step 3: Generate final aliases with conflict resolution
  final_aliases = {}

  for preferred_alias, conflicts in alias_map.items():
    if len(conflicts) == 1:
      # No conflict - use preferred name
      data = conflicts[0]
      final_alias = f"{work_folder_name}.{preferred_alias}"
      final_aliases[final_alias] = data["path"]
    else:
      # Resolve conflicts by adding minimal domain context
      for data in conflicts:
        path_parts = data["path_parts"]
        action_name = data["action_name"]

        if len(path_parts) == 1:
          # Root level - keep simple
          final_alias = f"{work_folder_name}.{preferred_alias}"
        elif len(path_parts) == 2:
          # capability/action - add domain prefix if needed
          final_alias = f"{work_folder_name}.{preferred_alias}"
        else:
          # domain/capability/action - add domain for disambiguation
          domain = to_slug_case(path_parts[0])
          capability = path_parts[-2]
          verb_noun = generate_verb_noun_name(action_name, capability)
          final_alias = f"{work_folder_name}.{domain}.{verb_noun}"

        # Handle remaining conflicts by adding more context
        original_alias = final_alias
        counter = 1
        while final_alias in final_aliases:
          if len(path_parts) > 2:
            # Add more parent directories
            extra_parts = (
              path_parts[: -(2 - counter)] if counter < len(path_parts) - 1 else path_parts[:-1]
            )
            domain_path = ".".join(to_slug_case(part) for part in extra_parts)
            capability = path_parts[-2]
            verb_noun = generate_verb_noun_name(action_name, capability)
            final_alias = f"{work_folder_name}.{domain_path}.{verb_noun}"
          else:
            # Fallback to numbering
            final_alias = f"{original_alias}.{counter}"
          counter += 1

        final_aliases[final_alias] = data["path"]

  # Create alias objects
  aliases = []
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
