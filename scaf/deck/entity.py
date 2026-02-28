from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from scaf.config import ALIASES_FILENAME, SCAF_FOLDER_NAME, SETTINGS_FILENAME
from scaf.core import Shape
from scaf.deck.rules import must_be_real_dir


@dataclass
class Deck(Shape):
  """Represents a location where scaf has been initialized, and provides access to its configuration files."""

  root: Path = field(doc="A folder where 'scaf init' has been run.")

  @cached_property
  def scaf_folder(self) -> Path:
    return self.root / SCAF_FOLDER_NAME

  @cached_property
  def aliases_file(self) -> Path:
    return self.scaf_folder / ALIASES_FILENAME

  @cached_property
  def settings_file(self) -> Path:
    return self.scaf_folder / SETTINGS_FILENAME

  def prepare(self):
    must_be_real_dir(self.scaf_folder)
