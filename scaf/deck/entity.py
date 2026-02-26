from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from scaf.config import ALIASES_FILENAME, SCAF_FOLDER_NAME, SETTINGS_FILENAME
from scaf.deck.rules import fit_root, must_be_real_dir
from scaf.core import Shape


@dataclass
class Deck(Shape):
  """Represents a location where scaf has been initialized, and provides access to its configuration files."""

  root: Path = field(
    metadata={"fitter": fit_root},
    doc="A folder where 'scaf init' has been run.",
  )

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
