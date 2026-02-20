from dataclasses import dataclass, field


@dataclass
class Test:
  """Run the tests. Raise on any failure."""

  def execute(self):
    from dev.test.handler import handle

    return handle(self)

  @dataclass
  class Result:
    """Define the shape of the value returned by Test below."""

    success: bool = field(doc="All tests passed without any failures.")
