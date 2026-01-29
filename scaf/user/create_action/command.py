from dataclasses import dataclass, field
from pathlib import Path

from scaf.user.create_action.rules import fit_action_method, fit_action_path, fit_description


@dataclass
class CreateAction:
  action_path: Path
  """e.g. 'cyberdyne/skynet/defense/fire_nukes`'"""
  action_method: str = field(default="command")
  """e.g. 'command' or 'query'"""
  description: str = field(default="")
  """e.g. 'Initiate the apocalypse.'"""

  def __post_init__(self):
    self.action_path = fit_action_path(self.action_path)
    self.action_method = fit_action_method(self.action_method)
    self.description = fit_description(self.description) or self.action_path.name
