import logging

from example.hole.insert_peg.command import InsertPeg

logger = logging.getLogger(__name__)


def handle(command: InsertPeg):
  logger.info(f"Inserting {command.peg} into {command.hole} (force={command.force})")
  if (
    command.peg.is_square()
    and command.hole.is_round()
    and command.peg.sides[0] > command.hole.sides[0]
    and not command.force
  ):
    logger.warning(f"Cannot insert {command.peg} into {command.hole} without force")
    return InsertPeg.Result(success=False)
  return InsertPeg.Result(success=True)
