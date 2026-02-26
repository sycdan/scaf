from dataclasses import dataclass, field
from pathlib import Path

from scaf.core import Shape


@dataclass
class SetConfig(Shape):
  """Set a configuration value for a domain, validated against its settings.py."""

  domain: Path = field(doc="Path to the domain folder (e.g. 'myapp/api').")
  setting: str = field(doc="Name of the setting to configure.")
  value: str = field(doc="Value to set (will be coerced to the field's declared type).")

  def execute(self):
    from scaf.user.config.set.handler import handle

    return handle(self)
