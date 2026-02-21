import logging

from scaf.config import SCAF_FOLDER_NAME
from scaf.deck.entity import Deck
from scaf.deck.locate.command import LocateDeck

logger = logging.getLogger(__name__)


def handle(command: LocateDeck):
  """If path is relative, only searches up to CWD."""
  logger.debug(f"Handling {command=}")
  for parent in command.path.parents:
    logger.debug(f"Checking for deck in {parent=}")
    scaf_folder = (parent / SCAF_FOLDER_NAME).resolve()
    if scaf_folder.exists() and scaf_folder.is_dir():
      logger.info(f"Found deck at {scaf_folder.parent.as_posix()}")
      return Deck(root=scaf_folder.parent)
  raise RuntimeError("No scaf deck found. Run 'scaf init' first.")
