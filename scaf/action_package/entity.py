from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import ModuleType

from scaf.tools import extract_first_dataclass


@dataclass
class ActionPackage:
  """A domain action loaded from the filesystem."""

  class DoesNotExist(FileNotFoundError):
    """Raised when the specified action package cannot be found."""

  action_folder: Path
  """Where `handler.py` is located."""
  init_module: ModuleType
  """Loaded from the `__init__.py` in the action folder."""
  shape_module: ModuleType
  """Loaded from `command.py` or `query.py`."""
  logic_module: ModuleType
  """Loaded from `handler.py`."""
  shape_class: type = field(init=False)
  """Frozen dataclass."""

  def __post_init__(self):
    """applies normalization and validation rules to input data"""
    self.shape_class = extract_first_dataclass(self.shape_module)

  @cached_property
  def action_method(self) -> str:
    """is either`command` or `query`"""
    return self.shape_module.__name__.split(".")[-1]
