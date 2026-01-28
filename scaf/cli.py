import argparse
import os
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


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Discover actions within a domain, or execute an action.",
    add_help=False,  # handled manually
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
  parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
  args, remaining = parser.parse_known_args(argv)

  if args.help and not args.call:
    return parser.print_help()

  try:
    if args.domain:
      root = ensure_absolute_path(args.domain)
    else:
      root = Path(__file__).parent  # scaf's internal domain

    if not root.exists():
      raise RuntimeError(f"Root does not exist: {root.as_posix()}")

    if args.call:
      action_package = LoadActionPackage(root, args.call).execute()
      if args.help:
        remaining.insert(0, "--help")
      pprint(CallAction(action_package, remaining).execute())
    else:
      for alias in GetAliases(root).execute():
        print(alias)
  except (ValueError, RuntimeError) as e:
    print_error(str(e))
    exit(1)
