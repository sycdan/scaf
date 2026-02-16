from dataclasses import dataclass


@dataclass
class Serve:
  """Start an app's backend. The code is not imported from the root of the repo, but is relative to the backend folder."""

  @dataclass
  class Result:
    pass
