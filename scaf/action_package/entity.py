from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import ModuleType

from scaf import config
from scaf.tools import compute_hash, extract_first_dataclass


@dataclass
class ActionPackage:
  """A domain action loaded from the filesystem."""

  action_dir: Path
  """Where `handler.py` is located."""
  init_module: ModuleType
  """Loaded from the `__init__.py` in the action folder."""
  shape_module: ModuleType
  """Loaded from `command.py` or `query.py`."""
  logic_module: ModuleType
  """Loaded from `handler.py`."""
  shape_class: type = field(init=False)
  """Frozen dataclass."""

  @cached_property
  def action_method(self) -> str:
    """is either`command` or `query`"""
    return self.shape_module.__name__.split(".")[-1]

  @cached_property
  def action_hash(self) -> str:
    """is based on the relative path to the action folder"""
    return compute_hash(self.action_dir.relative_to(config.ROOT_DIR))

  def __post_init__(self):
    """applies normalization and validation rules to input data"""
    self.shape_class = extract_first_dataclass(self.shape_module)
