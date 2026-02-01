from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Myriad:
  guid: UUID = field(default_factory=uuid4)
  boolean: bool = field(default=True)
  integer: int = field(default=42)
  text: str = field(default="hello")
  float: float = field(default=3.14)
