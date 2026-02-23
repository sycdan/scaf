from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TestTimestampHandling:
  timestamp: datetime | None = field(default=None, doc="Optional datetime argument")

  @dataclass
  class Result:
    type_name: str
    timestamp: datetime | None
