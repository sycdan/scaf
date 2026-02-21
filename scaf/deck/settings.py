from dataclasses import dataclass, field

from scaf import __version__


@dataclass
class Settings:
  version: str = field(default=__version__, doc="Scaf version that initialized this deck.")
