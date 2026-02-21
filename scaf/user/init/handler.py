import logging
from pathlib import Path
from string import Template

from scaf.alias.entity import Alias
from scaf.config import ALIASES_FILENAME
from scaf.deck.entity import Deck
from scaf.output import print_success
from scaf.tools import get_scaf_folder
from scaf.user.discover.command import Discover
from scaf.user.init.command import Init

logger = logging.getLogger(__name__)

ACTION_DIR = Path(__file__).parent
TEMPLATES_DIR = ACTION_DIR / "templates"


def get_alias_file(root: Path) -> Path:
  return get_scaf_folder(root) / ALIASES_FILENAME


def ensure_scaf_folder(root: Path) -> Path:
  scaf_folder = get_scaf_folder(root)
  if not scaf_folder.exists():
    scaf_folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created {scaf_folder.name} folder at: {root}")
  return scaf_folder


def parse_existing_action_paths(aliases_file: Path, root: Path) -> set[Path]:
  """Return the set of action paths already present in the aliases file, or empty if it doesn't exist."""
  known = set()
  if aliases_file.exists():
    for line in aliases_file.read_text(encoding="utf-8").splitlines():
      try:
        alias = Alias.from_bash(line.strip(), root=root)
        known.add(alias.action)
      except ValueError:
        continue
  return known


def ensure_aliases_file(deck: Deck, search_depth: int):
  root = deck.root
  aliases_file = get_alias_file(root)

  # When the file doesn't exist yet, existing_actions is empty, so all
  # discovered aliases are treated as new and written via the template.
  existing_actions = parse_existing_action_paths(aliases_file, root)

  if search_depth > 0:
    logger.info(
      f"Discovering actions (if this takes too long, try: scaf init {search_depth - 1})..."
    )
    result = Discover(deck=deck, depth=search_depth).execute()
    # Only keep aliases for action paths not already present; preserves manual renames.
    new_aliases = [a for a in result.aliases if a.action not in existing_actions]
  else:
    logger.info(f"Skipping action discovery ({search_depth=})")
    new_aliases = []

  if not aliases_file.exists():
    aliases_block = "\n".join(alias.to_bash() for alias in new_aliases)
    tmpl = Template((TEMPLATES_DIR / "aliases.tmpl").read_text(encoding="utf-8"))
    aliases_file.write_text(tmpl.substitute(aliases_block=aliases_block), encoding="utf-8")
    logger.info(f"Created aliases file: {aliases_file}")
  elif new_aliases:
    new_lines = "\n".join(alias.to_bash() for alias in new_aliases)
    existing_content = aliases_file.read_text(encoding="utf-8")
    aliases_file.write_text(
      existing_content.rstrip("\n") + "\n" + new_lines + "\n", encoding="utf-8"
    )
    logger.info(f"Added {len(new_aliases)} new alias(es)")
  else:
    logger.info("No new aliases to add")

  return aliases_file


def handle(command: Init):
  logger.debug(f"Handling {command=}")

  scaf_folder = ensure_scaf_folder(Path.cwd())
  deck = Deck(root=scaf_folder.parent)
  logger.debug(f"{deck=}")
  root = deck.root

  alias_file = ensure_aliases_file(deck, command.search_depth)

  lines = [
    f"Initialized scaf deck at: {root}",
    "",
    "💡 To activate aliases, add this to your shell/venv RC file:",
    "```bash",
    "# Load and display scaf aliases",
    f"source {alias_file.relative_to(root).as_posix()}",
    r"alias | grep -P --color=always '^(alias \K[^=]+)(?=.+scaf )'",
    "```",
    "ℹ️  When you create an action with 'scaf call', an alias for it will be added if not already present.",
  ]
  print_success("\n".join(lines))
