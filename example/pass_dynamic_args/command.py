from dataclasses import dataclass, field


@dataclass
class PassDynamicArgs:
  """Execute a tool call with dynamic arguments."""

  executable: str = field(
    doc="Path to executable",
  )

  @dataclass
  class Result:
    extra_args: list[str]
