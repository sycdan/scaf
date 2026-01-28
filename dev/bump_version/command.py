from dataclasses import dataclass


@dataclass
class BumpVersion:
  """Command to bump the app version using YYYY.MM.DD.NNNN format.

  Automatically increments build number for same-day versions.
  """

  pass
