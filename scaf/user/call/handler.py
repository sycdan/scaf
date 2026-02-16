import logging
import sys

from scaf.action_package.create.command import CreateActionPackage
from scaf.action_package.entity import ActionPackage
from scaf.action_package.invoke.command import InvokeActionPackage
from scaf.action_package.load.command import LoadActionPackage
from scaf.deck.entity import Deck
from scaf.deck.locate.command import LocateDeck
from scaf.user.call.command import Call

logger = logging.getLogger(__name__)


def ensure_import_path(deck: Deck):
  root = str(deck.root)  # sys.path seems to use str vs posix_path
  if root not in sys.path:
    logger.debug(f"Adding {root} to sys.path")
    sys.path.insert(0, root)


def handle(command: Call, *action_args):
  action = command.action

  if not (deck := LocateDeck(action=action).execute()):
    raise RuntimeError("No scaf deck found. Run 'scaf init' first.")
  ensure_import_path(deck)

  root = deck.root
  if action.is_absolute():
    action = action.relative_to(root)
  else:
    logger.debug(f"Resolving relative {action=} using deck {root=}")
    action = action.resolve().relative_to(root)

  logger.info(f"Calling {action.as_posix()} from {deck.root.as_posix()}")
  try:
    action_package = LoadActionPackage(root=root, action=action).execute()
  except ActionPackage.DoesNotExist:
    action_package = CreateActionPackage(deck=deck, action=action).execute()
  return InvokeActionPackage(action_package, list(action_args)).execute()
