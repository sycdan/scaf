import logging
from pathlib import Path

from api.serve.command import Serve

logger = logging.getLogger(__name__)

ACTION_DIR = Path(__file__).parent


def handle(command: Serve) -> Serve.Result:
  logger.debug(f"Handling {command=}")
  return Serve.Result()
