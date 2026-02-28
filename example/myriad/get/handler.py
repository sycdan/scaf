import logging

from example.myriad.entity import Myriad
from example.myriad.get.command import GetMyriad

logger = logging.getLogger(__name__)


def handle(command: GetMyriad):
  logger.debug(f"Handling {command=}")
  return Myriad()
