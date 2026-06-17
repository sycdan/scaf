from dataclasses import dataclass

from scaf.core import Shape


@dataclass
class Show(Shape):
  """List the aliases and descriptions of actions in the deck's alias file."""

  def execute(self):
    from scaf.user.show.handler import handle

    return handle(self)
