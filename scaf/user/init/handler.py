import logging
from pathlib import Path

from jinja2 import Template

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
  if aliases_file.exists():
    logger.info(f"Aliases file already exists at: {aliases_file}")
    return aliases_file

  logger.info("Gathering actions (if this takes too long, decrease search depth)...")
  result = Discover(deck=deck, depth=search_depth).execute()

  tmpl_path = TEMPLATES_DIR / "aliases.j2"
  tmpl = Template(tmpl_path.read_text(encoding="utf-8"))
  content = tmpl.render(aliases=result.aliases)

  aliases_file.write_text(content, encoding="utf-8")
  logger.info(f"Created aliases file: {aliases_file}")
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
