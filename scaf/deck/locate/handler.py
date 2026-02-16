from scaf.config import SCAF_FOLDER_NAME
from scaf.deck.entity import Deck
from scaf.deck.locate.command import LocateDeck


def handle(command: LocateDeck):
  """If the action is relative, we'll only look up to the CWD."""
  for parent in command.action.parents:
    scaf_folder = (parent / SCAF_FOLDER_NAME).resolve()
    if scaf_folder.exists() and scaf_folder.is_dir():
      return Deck(root=scaf_folder.parent)
  return None
