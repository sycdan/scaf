from dataclasses import dataclass, field
from pathlib import Path

from scaf.rules import values_must_fit


@dataclass
class LoadSettings:
  """Load settings for a domain, merging settings.py defaults with .scaf/settings.json overrides."""

  domain: Path = field(
    doc="Path to the domain, relative to deck root (e.g. 'project/workon' or 'scaf/user/init').",
  )

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.config.settings.load.handler import handle

    return handle(self)
