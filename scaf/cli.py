import argparse
import logging
import os
import sys
from pathlib import Path

from scaf.action.call.command import CallAction
from scaf.action_package.load.command import LoadActionPackage
from scaf.config import configure_logging
from scaf.core.get_aliases.query import GetAliases
from scaf.output import print_result

logger = logging.getLogger(__name__)


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
    return argv[0:index], remaining
  return argv[0:], []


def call(root: Path, action: Path | str, *args):
  if not isinstance(action, Path):
    action = Path(action)
  logger.info(f"Calling action '{action.as_posix()}' from {root.as_posix()}")
  action_package = LoadActionPackage(root, action).execute()
  return CallAction(action_package, list(args)).execute()


def main(argv=None):
  argv, remaining = split_argv(list(argv or sys.argv[1:]))
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
  parser.add_argument(
    "--verbose",
    "-v",
    action="count",
    default=0,
    help="Increase output verbosity (can be used multiple times).",
  )
  args: argparse.Namespace = parser.parse_args(argv)
  configure_logging(args.verbose)

  try:
    if args.domain:
      root = ensure_absolute_path(args.domain)
      action_filter = ""
    else:
      root = Path(__file__).parent.parent  # scaf's code root
      action_filter = "scaf/user"

    if not root.exists():
      raise RuntimeError(f"Root does not exist: {root.as_posix()}")

    if action := args.call:
      print_result(call(root, action, *remaining))
    else:
      logger.info(f"Listing actions in domain at: {root.as_posix()}")
      for alias in GetAliases(root, filter=action_filter).execute():
        print(alias)
  except (ValueError, RuntimeError) as e:
    logger.error(str(e))
    exit(1)
