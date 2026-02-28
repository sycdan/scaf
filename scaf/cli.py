import argparse
import logging
import os
import sys
from pathlib import Path

import scaf
from scaf.config import configure_logging
from scaf.output import print_result

logger = logging.getLogger(__name__)

USER_ROOT = Path(scaf.__file__).parent / "user"


def _discover_user_actions() -> list[Path]:
  from scaf.user.discover.handler import find_available_actions

  return find_available_actions(USER_ROOT, max_depth=2)


def _print_help(actions: list[Path]) -> None:
  from scaf.action_package.load.command import LoadActionPackage

  print("Usage: scaf [--verbose] <command> [args...]")
  print()
  print("Available commands:")
  for action in actions:
    try:
      pkg = LoadActionPackage(root=USER_ROOT, action=action).execute()
      doc = (pkg.shape_class.__doc__ or "").strip().splitlines()[0]
    except Exception:
      doc = ""
    print(f"  {action.as_posix():<20} {doc}")


def main(argv=None):
  # Parse global flags only; leave everything else for action dispatch
  flag_parser = argparse.ArgumentParser(add_help=False, prog="scaf")
  flag_parser.add_argument(
    "--verbose",
    "-v",
    action="count",
    default=0,
    help="Increase output verbosity (can be used multiple times).",
  )
  flag_args, remaining = flag_parser.parse_known_args(argv or sys.argv[1:])
  configure_logging(flag_args.verbose or int(os.getenv("SCAF_VERBOSITY", 0)))

  actions = _discover_user_actions()
  action_posix_set = {a.as_posix() for a in actions}

  # Greedily match the longest prefix of non-flag tokens to a known action path
  matched_action: Path | None = None
  rest_start = 0
  command_parts: list[str] = []

  for i, token in enumerate(remaining):
    if token.startswith("-"):
      break
    command_parts.append(token)
    candidate = "/".join(command_parts)
    if candidate in action_posix_set:
      matched_action = Path(candidate)
      rest_start = i + 1

  if matched_action is None:
    _print_help(actions)
    return

  action_args = remaining[rest_start:]

  try:
    from scaf.action_package.invoke.command import InvokeActionPackage
    from scaf.action_package.load.command import LoadActionPackage

    pkg = LoadActionPackage(root=USER_ROOT, action=matched_action).execute()
    result = InvokeActionPackage(pkg, action_args).execute()
    if result is not None:
      print_result(result)
  except (ValueError, RuntimeError) as e:
    logger.error(str(e))
    exit(1)
