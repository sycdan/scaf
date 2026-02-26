from dataclasses import dataclass, field
from pathlib import Path

from scaf.core import Shape


@dataclass
class LoadSettings(Shape):
  """Load settings for a domain, merging settings.py defaults with .scaf/settings.json overrides."""

  domain: Path = field(
    doc="Path to the domain, relative to deck root (e.g. 'project/workon' or 'scaf/user/init').",
  )

  def execute(self):
    from scaf.config.settings.load.handler import handle

    return handle(self)
