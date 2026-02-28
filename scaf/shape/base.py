import inspect
import logging
from dataclasses import dataclass

from scaf.rules import values_must_fit

logger = logging.getLogger(__name__)


@dataclass
class Shape:
  """Base class for dataclasses that define the structure of domain actions."""

  def __post_init__(self):
    logger.debug(f"👋 {type(self).__name__}.{self.__post_init__.__name__}")
    values_must_fit(self)
    if prepare := getattr(type(self), "prepare", None):
      logger.debug(f"📞 {type(self).__name__}.{prepare.__name__} @ {inspect.getmodule(prepare)}")
      prepare(self)
