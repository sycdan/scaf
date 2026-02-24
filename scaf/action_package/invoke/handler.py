import argparse
import dataclasses
import inspect
import logging
from pathlib import Path

from scaf.action_package.invoke.command import InvokeActionPackage
from scaf.tools import get_acceptable_types, get_fitter, to_slug_case

logger = logging.getLogger(__name__)


def build_parser_from_shape(shape_class: type, description: str):
  logger.debug(
    f"Building argparse parser from shape class {shape_class} with description: {description}"
  )
  parser = argparse.ArgumentParser(description=description)

  for field in dataclasses.fields(shape_class):
    logger.debug(
      f"Processing field {field.name} of type {field.type} with default {field.default}"
    )
    name = field.name
    t, _, _ = get_acceptable_types(field)
    fitter = get_fitter(shape_class, name)
    default = field.default
    help = field.doc or ""

    if default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
      # required positional
      parser.add_argument(name, type=fitter, help=help)
    else:
      # optional with default or default_factory
      flag_name = to_slug_case(name)
      if t is bool:
        # For bool fields, use the default or False if default_factory
        effective_default = default if default is not dataclasses.MISSING else False
        parser.add_argument(
          f"--{flag_name}", action="store_true", default=effective_default, dest=name, help=help
        )
      else:
        # For non-bool fields, use the default or call default_factory if available
        if default is not dataclasses.MISSING:
          effective_default = default
        else:
          # default_factory exists, call it to get the default value
          effective_default = field.default_factory()  # type: ignore
        parser.add_argument(
          f"--{flag_name}", type=fitter, default=effective_default, dest=name, help=help
        )

  return parser


def handle(command: InvokeActionPackage):
  logger.debug(f"Handling {command=}")

  action_package = command.action_package
  action_folder = action_package.action_folder
  shape_class = action_package.shape_class

  description = shape_class.__doc__ or action_package.shape_module.__doc__ or "Do the thing."
  action_parser = build_parser_from_shape(shape_class, description=description)

  if action_folder.is_relative_to(Path.cwd()):
    action_path = action_folder.relative_to(Path.cwd())
  else:
    action_path = action_folder
  action_parser.prog = f"scaf call {action_path.as_posix()}"

  try:
    args, extra_args = action_parser.parse_known_args(command.action_args)
  except SystemExit as e:
    if not e.code:
      return  # help was shown
    raise RuntimeError("Invalid action arguments.")

  action = shape_class(**vars(args))

  if extra_args:
    sig = inspect.signature(action_package.logic_module.handle)
    accepts_var_positional = any(
      p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()
    )
    if not accepts_var_positional:
      raise RuntimeError(f"Unexpected arguments: {extra_args}")

  return action_package.logic_module.handle(action, *extra_args)
