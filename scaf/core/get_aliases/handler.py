"""Constructs bash aliases for action packages in a domain/capability."""

import logging
import os
from pathlib import Path

from scaf.action_package.rules import must_contain_required_files
from scaf.alias.entity import Alias
from scaf.core.get_aliases.query import GetAliases
from scaf.tools import to_slug_case

logger = logging.getLogger(__name__)


def load_scafignore(domain_folder: Path) -> list[str]:
  """Load .scafignore file from domain folder, if it exists."""
  ignore_file = domain_folder / ".scafignore"
  ignore_patterns = []
  if ignore_file.exists():
    with ignore_file.open("r", encoding="utf-8") as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
          ignore_patterns.append(line)
    logger.info("Loaded .scafignore with %d pattern(s)", len(ignore_patterns))
  return ignore_patterns


def find_available_actions(domain_folder: Path) -> list[str]:
  logger.info("Searching for action packages in domain folder: %s", domain_folder.as_posix())
  ignore_patterns = load_scafignore(domain_folder)
  actions = []
  for base, dirs, files in os.walk(domain_folder):
    # Skip hidden directories and __pycache__ etc.
    dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]
    # Apply .scafignore patterns
    relative_base = Path(base).relative_to(domain_folder).as_posix()
    if any(Path(relative_base).match(pattern) for pattern in ignore_patterns):
      logger.debug("Ignoring folder due to .scafignore: %s", relative_base)
      continue
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
  logger.info("Generating aliases for %d actions", len(action_paths))
  work_folder_name = root.name

  # Step 1: Generate preferred alias for each action
  action_data = []
  for action_path in action_paths:
    path_parts = action_path.split("/")
    action_name = path_parts[-1]

    if len(path_parts) == 1:
      # Root level action - use repo name prefix
      preferred_alias = to_slug_case(action_name)
      alias_prefix = work_folder_name
    elif len(path_parts) == 2:
      # domain/action pattern - use domain prefix, simple action name
      domain = path_parts[0]
      preferred_alias = to_slug_case(action_name)
      alias_prefix = to_slug_case(domain)
    else:
      # domain/capability/action or deeper
      domain = path_parts[0]
      capability = path_parts[-2]

      # Don't automatically include capability - only add during conflict resolution
      # Generate simple preferred alias first, add capability only if conflicts exist
      if "_" in action_name:
        preferred_alias = to_slug_case(action_name)
      else:
        # For single verb actions, create verb-capability
        preferred_alias = generate_verb_noun_name(action_name, capability)

      alias_prefix = to_slug_case(domain)

    action_data.append(
      {
        "path": action_path,
        "path_parts": path_parts,
        "preferred_alias": preferred_alias,
        "action_name": action_name,
        "alias_prefix": alias_prefix,
      }
    )

  # Step 2: Detect conflicts and resolve with minimal path inclusion
  alias_map = {}
  for data in action_data:
    full_alias = f"{data['alias_prefix']}.{data['preferred_alias']}"
    if full_alias not in alias_map:
      alias_map[full_alias] = []
    alias_map[full_alias].append(data)

  # Step 3: Generate final aliases with conflict resolution
  final_aliases = {}

  for full_alias, conflicts in alias_map.items():
    if len(conflicts) == 1:
      # No conflict - use preferred name
      data = conflicts[0]
      final_aliases[full_alias] = data["path"]
    else:
      # Resolve conflicts by adding more specificity
      for data in conflicts:
        path_parts = data["path_parts"]
        action_name = data["action_name"]
        alias_prefix = data["alias_prefix"]

        if len(path_parts) <= 2:
          # Shouldn't have conflicts at this level, use original
          final_alias = f"{alias_prefix}.{data['preferred_alias']}"
        else:
          # domain/capability/action - add capability for disambiguation
          capability = to_slug_case(path_parts[-2])

          if "_" in action_name:
            # verb_noun action needs capability prefix for conflicts
            final_alias = f"{alias_prefix}.{capability}.{to_slug_case(action_name)}"
          else:
            # verb action - use verb-capability pattern
            verb_noun = generate_verb_noun_name(action_name, path_parts[-2])
            final_alias = f"{alias_prefix}.{verb_noun}"

        # Handle remaining conflicts by adding more context
        original_alias = final_alias
        counter = 1
        while final_alias in final_aliases:
          # Fallback to numbering for rare edge cases
          final_alias = f"{original_alias}.{counter}"
          counter += 1

        final_aliases[final_alias] = data["path"]

  # Create alias objects
  aliases = []
  for alias_name, action_path in sorted(final_aliases.items()):
    aliases.append(Alias(name=alias_name, root=root, action=Path(action_path)))

  return aliases


def handle(command: GetAliases) -> list[Alias]:
  actions = find_available_actions(command.root)
  aliases = generate_action_aliases(command.root, actions)
  if command.filter:
    aliases = [a for a in aliases if a.action.as_posix().startswith(command.filter)]
  return aliases
