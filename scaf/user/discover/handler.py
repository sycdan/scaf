import logging
import sys
from pathlib import Path

from scaf.action_package.entity import ActionPackage
from scaf.action_package.load.command import LoadActionPackage
from scaf.action_package.rules import must_contain_required_files
from scaf.alias.entity import Alias
from scaf.alias.tools import append_aliases, parse_all_aliases
from scaf.output import NC, RED
from scaf.tools import to_dot_path, to_slug_case
from scaf.user.call.handler import ensure_import_path
from scaf.user.discover.command import Discover

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


def find_available_actions(root: Path, max_depth: int) -> list[Path]:
  logger.info("Searching for action packages in domain folder: %s", root.as_posix())
  ignore_patterns = load_scafignore(root)
  actions = []

  for base, dirs, files in root.walk():
    if base == root:
      continue  # Skip root

    if base.name.startswith(".") or base.name.startswith("_"):
      continue  # Skip hidden/private folders

    if not files:
      continue  # Skip folders without files, as they can't be action packages

    logger.debug(f"{base=}, {dirs=}, {files=}")
    folder = base.relative_to(root)
    depth = len(folder.parts)

    if depth > max_depth:
      dirs[:] = []  # Don't recurse further into this directory
      continue
    elif depth > 0:  # Skip root
      # Apply ignore patterns, e.g. temp* or */logs
      if any(folder.match(pattern) for pattern in ignore_patterns):
        logger.debug("Ignoring folder due to .scafignore: %s", folder)
        continue

      try:
        must_contain_required_files(files)
        actions.append(folder)
      except ValueError:
        continue

  return sorted(actions)


# TODO: use this
def generate_verb_noun_name(action_name: str, capability: str) -> str:
  """Generate verb-noun pattern from action and capability names."""
  action_slug = to_slug_case(action_name)
  capability_slug = to_slug_case(capability)

  # If action contains underscore, it's already verb_noun -> verb-noun
  if "_" in action_name:
    return action_slug

  # Single verb + capability -> verb-capability
  return f"{action_slug}-{capability_slug}"


def generate_alias_name(root: Path, action_package: ActionPackage) -> str:
  # TODO: handle capable entities
  return to_dot_path(action_package.action_folder.relative_to(root)).replace("_", "-")


def generate_action_aliases(root: Path, actions: list[Path], filter="") -> list[Alias]:
  logger.info("Generating aliases for %d actions", len(actions))
  aliases: list[Alias] = []

  for action in actions:
    if filter and not action.match(filter):
      logger.debug("Skipping action '%s' due to filter '%s'", action, filter)
      continue

    try:
      ap = LoadActionPackage(root=root, action=action).execute()
    except Exception as e:
      logger.warning("Failed to load action package %s: %s", action, e)
      continue

    alias_name = generate_alias_name(root, ap)
    aliases.append(Alias(name=alias_name, root=root, action=action))

  return aliases


def _get_docstring(alias: Alias, root: Path) -> str:
  """Load the action package for an alias and return the shape docstring."""
  try:
    ap = LoadActionPackage(root=root, action=alias.action).execute()
    doc = (ap.shape_class.__doc__ or ap.shape_module.__doc__ or "").strip().splitlines()[0]
    return doc
  except Exception:
    return ""


def _print_alias_listing(aliases: list[Alias], root: Path) -> None:
  """Print each alias name in red followed by its docstring to stderr."""
  for alias in aliases:
    doc = _get_docstring(alias, root)
    raw_cmd = alias.to_bash()
    logger.info("  %s", raw_cmd)
    print(f"{RED}{alias.name}{NC}  {doc}", file=sys.stderr)


def handle(command: Discover):
  deck = command.deck
  ensure_import_path(deck)

  # Discover available actions and generate aliases for them
  actions = find_available_actions(deck.root, command.depth)
  discovered_aliases = generate_action_aliases(deck.root, actions, command.filter)

  if not command.user:
    # Internal call (e.g. from init): just return discovered aliases; caller owns the file
    return command.Result(aliases=discovered_aliases)

  aliases_file = deck.aliases_file
  if not aliases_file.exists():
    logger.error("No aliases file found at %s. Run 'scaf init' to create one.", aliases_file)
    sys.exit(1)

  # Write new aliases (not already present) to the deck's aliases file
  existing_actions = {a.action for a in parse_all_aliases(aliases_file, deck.root)}
  new_aliases = [a for a in discovered_aliases if a.action not in existing_actions]
  append_aliases(aliases_file, new_aliases)

  # Re-parse the full file so the listing reflects renames by the user
  all_aliases = parse_all_aliases(aliases_file, deck.root)
  _print_alias_listing(all_aliases, deck.root)
  sys.exit(0)
