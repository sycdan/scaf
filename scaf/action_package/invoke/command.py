from dataclasses import dataclass, field

from scaf.action_package.entity import ActionPackage


@dataclass
class InvokeActionPackage:
  action_package: ActionPackage
  action_args: list[str] = field(default_factory=list)

  def execute(self):
    from scaf.action_package.invoke.handler import handle

    return handle(self)
