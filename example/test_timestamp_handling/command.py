from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestTimestampHandling:
  timestamp: datetime | str
  """For now, we must allow this to be a string to work around the fact that there is no timestamp parsing logic. This is something we should eventually fix."""

  @dataclass
  class Result:
    type_name: str
    timestamp: str
