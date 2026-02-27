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

  show_scaf_help = remaining and remaining[0] in ("--help", "-h")

  try:
    if command == "init":
      init_parser = argparse.ArgumentParser(
        description="Initialize a scaf deck in the working directory.",
        prog="scaf init",
      )
      init_parser.add_argument(
        "search_depth",
        nargs="?",
        type=int,
        default=0,
        help="How far to search for existing actions.",
      )
      if show_scaf_help:
        init_parser.print_help()
        return
      init_args = init_parser.parse_args(remaining)
      return Init(**vars(init_args)).execute()
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
      init_parser = argparse.ArgumentParser(
        description="Call a domain action.",
        prog="scaf call",
      )
      init_parser.add_argument("action", help="Path to the action to invoke.")
      init_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to pass to the action."
      )
      if show_scaf_help:
        init_parser.print_help()
        return
      init_args = init_parser.parse_args(remaining)
      return print_result(Call(**vars(init_args)).execute())
    else:
      raise ValueError(f"Unknown command: {command}")
  except (ValueError, RuntimeError) as e:
    logger.error(str(e))
    exit(1)
