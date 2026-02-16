from dataclasses import dataclass, field

from scaf.action_package.entity import ActionPackage
from scaf.rules import values_must_fit


@dataclass
class InvokeActionPackage:
  action_package: ActionPackage
  action_args: list[str] = field(default_factory=list)

  def __post_init__(self):
    values_must_fit(self)

  def execute(self):
    from scaf.action_package.invoke.handler import handle

    return handle(self)
