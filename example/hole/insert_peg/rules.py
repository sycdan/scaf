import logging

from example.thing.entity import Thing

logger = logging.getLogger(__name__)


def _parse_thing(value) -> Thing:
  """Parse a comma-separated list of ints into a Thing, e.g. '4,4,4,4'."""
  if isinstance(value, Thing):
    return value
  logger.debug(f"Parsing {Thing} from value: %r", value)
  sides = [int(s.strip()) for s in str(value).split(",")]
  return Thing(sides=sides)


def fit_peg(value) -> Thing:
  return _parse_thing(value)


def fit_hole(value) -> Thing:
  return _parse_thing(value)
