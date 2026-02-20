from dataclasses import dataclass, field


@dataclass
class Dev:
  """Describe the Dev entity."""

  name: str = field(
    default_factory=lambda: __import__("getpass").getuser(),
    doc="The name of the dev.",
  )
