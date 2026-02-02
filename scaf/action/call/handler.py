import argparse
import dataclasses
import logging
import typing
from typing import get_args, get_origin

from scaf.action.call.command import CallAction
from scaf.config import set_root_dir
from scaf.tools import to_slug_case

logger = logging.getLogger(__name__)


def normalize_argparse_type(t):
  logger.debug(msg=f"Normalizing type {t} for argparse")
  origin = get_origin(t)

  # Optional[T] or Union[T, None]
  if origin is typing.Union:
    logger.debug(f"{origin=}")
    types = [a for a in get_args(t) if a is not type(None)]
    if len(types) > 0:
      return normalize_argparse_type(types[-1])

    # fallback to string
    return str

  # bare type
  return t


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
    type_ = normalize_argparse_type(field.type)
    logger.debug(f"Normalized type for field '{name}': {type_}")
    default = field.default

    if default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
      # required positional
      parser.add_argument(name, type=type_)
    else:
      # optional with default or default_factory
      flag_name = to_slug_case(name)
      if type_ is bool:
        # For bool fields, use the default or False if default_factory
        effective_default = default if default is not dataclasses.MISSING else False
        parser.add_argument(
          f"--{flag_name}", action="store_true", default=effective_default, dest=name
        )
      else:
        # For non-bool fields, use the default or call default_factory if available
        if default is not dataclasses.MISSING:
          effective_default = default
        else:
          # default_factory exists, call it to get the default value
          effective_default = field.default_factory()  # type: ignore
        parser.add_argument(f"--{flag_name}", type=type_, default=effective_default, dest=name)

  return parser


def handle(command: CallAction):
  logger.debug(f"Handling {command=}")
  root = command.action_package.root
  set_root_dir(root)

  domain_action = command.action_package
  description = domain_action.init_module.__doc__ or "No comment."

  shape_class = domain_action.shape_class
  action_parser = build_parser_from_shape(shape_class, description=description)
  action_parser.prog = (
    f"scaf {root.as_posix()} --call {domain_action.action_folder.relative_to(root).as_posix()}"
  )

  try:
    args, extra_args = action_parser.parse_known_args(command.action_args)
  except SystemExit as e:
    if not e.code:
      return  # help was shown
    raise RuntimeError("Invalid action arguments.")

  action = shape_class(**vars(args))
  return domain_action.logic_module.handle(action, *extra_args)
