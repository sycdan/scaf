import logging

from scaf.deck.entity import Deck
from scaf.deck.rules import fit_root

logger = logging.getLogger(__name__)


def fit_deck(value) -> Deck:
  if isinstance(value, Deck):
    return value
  logger.debug(f"func={fit_deck.__name__} {value=}")
  return Deck(root=fit_root(value))
