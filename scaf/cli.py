import argparse
import os
import sys
from pathlib import Path
from pprint import pprint

from scaf.action.call.command import CallAction
from scaf.action_package.load.command import LoadActionPackage
from scaf.core.get_aliases.query import GetAliases
from scaf.output import print_error


def ensure_absolute_path(path: Path | str) -> Path:
  path = Path(path)
  if not path.is_absolute():
    path = Path(os.getcwd()) / path
  return path


def split_argv(argv: list[str]) -> tuple[list[str], list[str]]:
  """manually stop grabbing scaf args at the first "--" since argparse doesn't do it how we need"""
  if "--" in argv:
    index = argv.index("--")
    remaining = argv[index + 1 :]
    return argv[1:index], remaining
  return argv[1:], []


def main(argv=None):
  argv, remaining = split_argv(list(argv or sys.argv))
  parser = argparse.ArgumentParser(
    description="Discover actions within a domain, or execute an action.",
    prog="scaf",
  )
  parser.add_argument(
    "domain",
    nargs="?",
    default="",
    help="Where to import domain actions from. Omit to use scaf's internal domain.",
  )
  parser.add_argument(
    "--call",
    default="",
    help="Execute the domain action at this path. Additional args are passed to the action.",
  )
  args = parser.parse_args(argv)

  try:
    if args.domain:
      root = ensure_absolute_path(args.domain)
      alias_filter = ""
    else:
      root = Path(__file__).parent  # scaf's internal domain
      alias_filter = "user/"

    if not root.exists():
      raise RuntimeError(f"Root does not exist: {root.as_posix()}")

    if args.call:
      action_package = LoadActionPackage(root, args.call).execute()
      pprint(CallAction(action_package, remaining).execute())
    else:
      for alias in GetAliases(root, filter=alias_filter).execute():
        print(alias)
  except (ValueError, RuntimeError) as e:
    print_error(str(e))
    exit(1)
