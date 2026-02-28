import logging
import sys
from pathlib import Path
from string import Template

from scaf.alias.tools import append_aliases, parse_all_aliases
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


def ensure_aliases_file(deck: Deck, search_depth: int):
  root = deck.root
  aliases_file = get_alias_file(root)

  if not aliases_file.exists():
    tmpl = Template((TEMPLATES_DIR / "aliases.tmpl").read_text(encoding="utf-8"))
    aliases_file.write_text(tmpl.safe_substitute(), encoding="utf-8")
    logger.info(f"Created aliases file: {aliases_file}")

  if search_depth > 0:
    logger.info(
      f"Discovering actions (if this takes too long, run 'scaf init {search_depth - 1}')..."
    )
    result = Discover(deck=deck, depth=search_depth, user=False).execute()
    existing_actions = {a.action for a in parse_all_aliases(aliases_file, root)}
    new_aliases = [a for a in result.aliases if a.action not in existing_actions]
    append_aliases(aliases_file, new_aliases)
  else:
    logger.info(f"Skipping action discovery ({search_depth=})")

  return aliases_file


def handle(command: Init):
  logger.debug(f"Handling {command=}")

  scaf_folder = ensure_scaf_folder(Path.cwd())
  deck = Deck(root=scaf_folder.parent)
  logger.debug(f"{deck=}")
  root = deck.root

  alias_file = ensure_aliases_file(deck, command.search_depth)

  lines = [
    f"Initialized scaf deck at {root}",
    "",
    "💡 To activate aliases, add this to your shell/venv RC file:",
    "```bash",
    "# Load and display scaf aliases",
    f"scaf discover . && source {alias_file.relative_to(root).as_posix()}",
    "```",
    "ℹ️  After creating an action, remember to refresh your environment to pick up the new alias.",
  ]
  print_success("\n".join(lines))
  sys.exit(0)
