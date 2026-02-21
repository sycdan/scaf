from dataclasses import dataclass, field
from pathlib import Path

from scaf.rules import values_must_fit


@dataclass
class SetConfig:
  """Set a configuration value for a domain, validated against its settings.py."""

  domain: Path = field(doc="Path to the domain folder (e.g. 'myapp/api').")
  setting: str = field(doc="Name of the setting to configure.")
  value: str = field(doc="Value to set (will be coerced to the field's declared type).")

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.user.config.set.handler import handle

    return handle(self)
