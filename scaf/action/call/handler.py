import argparse
import dataclasses
import typing
from typing import get_args, get_origin

from scaf.action.call.command import CallAction
from scaf.config import set_root_dir
from scaf.tools import to_slug_case


def normalize_argparse_type(t):
  origin = get_origin(t)

  # Optional[T] or Union[T, None]
  if origin is typing.Union:
    args = [a for a in get_args(t) if a is not type(None)]
    if len(args) == 1:
      return normalize_argparse_type(args[0])
    # fallback: treat as string
    return str

  # bare type
  return t


def build_parser_from_shape(shape_class: type, description: str):
  parser = argparse.ArgumentParser(description=description)

  for field in dataclasses.fields(shape_class):
    name = field.name
    type_ = normalize_argparse_type(field.type)
    default = field.default

    if default is dataclasses.MISSING:
      # required positional
      parser.add_argument(name, type=type_)
    else:
      flag_name = to_slug_case(name)
      if type_ is bool:
        parser.add_argument(f"--{flag_name}", action="store_true", default=default, dest=name)
      else:
        parser.add_argument(f"--{flag_name}", type=type_, default=default, dest=name)

  return parser


def handle(command: CallAction):
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
    args = action_parser.parse_args(command.action_args)
  except SystemExit as e:
    if not e.code:
      return  # help was shown
    raise RuntimeError("Invalid action arguments.")

  action = shape_class(**vars(args))
  return domain_action.logic_module.handle(action)
