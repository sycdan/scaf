from dataclasses import dataclass, field

from scaf.action_package.entity import ActionPackage


@dataclass
class CallAction:
  action_package: ActionPackage
  action_args: list[str] = field(default_factory=list)

  def execute(self):
    from scaf.action.call.handler import handle

    return handle(self)
