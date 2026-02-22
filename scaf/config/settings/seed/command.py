from dataclasses import dataclass, field
from pathlib import Path

from scaf.rules import values_must_fit


@dataclass
class SeedSettings:
  """Create a settings.py for a domain using the default template, seeded with one field."""

  domain_path: Path = field(doc="Absolute path to the domain folder.")
  setting: str = field(doc="Name of the initial setting field to add.")
  value: str = field(doc="Default value for the initial setting (stored as str).")

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.config.settings.seed.handler import handle

    return handle(self)
