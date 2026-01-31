from dataclasses import dataclass, field


@dataclass
class PassDynamicArgs:
  """Executes a tool with dynamic arguments that should be passed through."""

  executable: str = field(
    metadata={"help": "Path to executable"},
  )
