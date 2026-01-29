from dataclasses import dataclass


@dataclass
class Alias:
  name: str
  scaf_args: str

  @classmethod
  def from_raw(cls, raw: str) -> "Alias":
    # e.g.: alias scaf.call='scaf C:/Users/Dan/Projects/scaf/scaf/action/call'
    assert raw.startswith("alias "), f"Invalid alias format: {raw}"
    raw = raw[6:]
    name, command = raw.split("=", 1)
    command = command.strip("'\"")
    assert command.startswith("scaf "), f"Invalid alias command: {command}"
    command = command[5:]
    return cls(name=name, scaf_args=command)
