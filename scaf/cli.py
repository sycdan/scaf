import argparse
import logging
import os
import sys

import scaf
from scaf.config import configure_logging
from scaf.output import print_result
from scaf.user.call.command import Call
from scaf.user.config.set.command import SetConfig
from scaf.user.init.command import Init

logger = logging.getLogger(__name__)


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="What do you want to do?",
    prog="scaf",
    add_help=False,
  )
  parser.add_argument(
    "--verbose",
    "-v",
    action="count",
    default=0,
    help="Increase output verbosity (can be used multiple times).",
  )
  parser.add_argument(
    "command",
    choices=["init", "version", "call", "config"],
    nargs="?",
    help="Specify the command to execute. When calling an action, add -h for help.",
  )
  args, remaining = parser.parse_known_args(argv or sys.argv[1:])
  configure_logging(args.verbose or int(os.getenv("SCAF_VERBOSITY", 0)))

  if not (command := (args.command or "").strip().lower()):
    return parser.print_help()

  try:
    if command == "init":
      init_kwargs = {}
      try:
        init_kwargs["search_depth"] = remaining.pop(0)
      except IndexError:
        pass
      return Init(**init_kwargs).execute()
    if command == "version":
      return print(scaf.__version__)
    if command == "config":
      subcommand = remaining.pop(0) if remaining else ""
      if subcommand == "set":
        set_config_kwargs = {}
        try:
          set_config_kwargs.update(
            {
              "domain": remaining[0],
              "setting": remaining[1],
              "value": remaining[2],
            }
          )
        except IndexError:
          raise ValueError("Usage: scaf config set <domain> <setting> <value>")
        return SetConfig(**set_config_kwargs).execute()
      raise ValueError(f"Unknown config subcommand: {subcommand!r}. Available: set")
    if command == "call":
      call_kwargs = {}
      try:
        call_kwargs["action"] = remaining.pop(0)
      except IndexError:
        raise ValueError("No action specified. Usage: scaf call <path/to/action> [args...]")
      return print_result(Call(**call_kwargs).execute(*remaining))
    else:
      raise ValueError(f"Unknown command: {command}")
  except (ValueError, RuntimeError) as e:
    logger.error(str(e))
    exit(1)
