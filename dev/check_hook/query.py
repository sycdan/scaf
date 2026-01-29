from dataclasses import dataclass


@dataclass
class CheckHook:
  """Check if the installed git pre-push hook matches the source version."""

  def execute(self):
    from dev.check_hook.handler import handle

    return handle(self)
