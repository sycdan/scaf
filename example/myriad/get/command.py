from dataclasses import dataclass


@dataclass
class GetMyriad:
  """demonstrates simple json serialization of action responses."""

  def execute(self):
    from example.myriad.get.handler import handle

    return handle(self)
