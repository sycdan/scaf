import sys

from example.hole.insert_peg.command import InsertPeg


def handle(command: InsertPeg):
  result = {"peg": command.peg, "hole": command.hole, "force_insert": command.force_insert}
  print(
    f"Inserting {command.peg} into {command.hole}, force={command.force_insert}", file=sys.stderr
  )
  return result
