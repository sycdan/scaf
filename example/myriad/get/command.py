from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class GetMyriad:
  """Demonstrate simple json serialization of action responses."""

  inferred_optional: int | None = field(
    default=None,
    doc="is the preferred way to add help text",
  )
  explicit_optional: Optional[int] = field(
    default=None,
    metadata={"help": "help metadata is deprecated; use field(doc=...) instead"},
  )
  explicit_union: Union[int, str] = field(
    default=42,
    metadata={"help": "int is preferred, but we'll take a string for backwards compatibility"},
  )

  def execute(self):
    from example.myriad.get.handler import handle

    return handle(self)
