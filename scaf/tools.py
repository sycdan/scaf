"""May touch filesystem, but not DB or network."""

import logging
import re
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import get_origin

from scaf.config import SCAF_FOLDER_NAME

logger = logging.getLogger(__name__)


def compute_hash(path: Path) -> str:
  return sha256(path.as_posix().encode("utf-8")).hexdigest()


def to_snake_case(name):
  # Insert underscores before capital letters (except at start)
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
  # Insert underscores before capital letters preceded by lowercase or digits
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
  # Replace any non-alphanumeric with underscores and clean up
  return re.sub(r"[^a-zA-Z0-9]+", "_", s2).strip("_").lower()


def to_camel_case(name):
  # First split on capital letters to handle CamelCase input
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", name)
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)
  # Then split on non-alphanumeric and capitalize each word
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", s2) if word)


def to_slug_case(name):
  # Insert hyphens before capital letters (except at start)
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
  # Insert hyphens before capital letters preceded by lowercase or digits
  s2 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1)
  # Replace any non-alphanumeric with hyphens and clean up
  return re.sub(r"[^a-zA-Z0-9]+", "-", s2).strip("-").lower()


def to_dot_path(path: Path):
  if path.as_posix() == ".":
    raise ValueError("Path cannot be empty")
  return ".".join(path.as_posix().split("/"))


def extract_first_dataclass(module: ModuleType) -> type:
  for name, obj in vars(module).items():
    if isinstance(obj, type) and not name.startswith("_"):
      if hasattr(obj, "__dataclass_fields__") and obj.__module__ == module.__name__:
        return obj
  raise ValueError(f"No dataclass found in {module.__file__}")


def get_fitter(for_class: type, field_name: str):
  try:
    fields = for_class.__dataclass_fields__
  except AttributeError:
    logger.warning(f"Failed to get fitter for {field_name}. {for_class} is not a dataclass.")
    return lambda x: x

  try:
    field = fields[field_name]
  except KeyError:
    logger.warning(f"Failed to get fitter for {field_name}. Field not found in {for_class}.")
    return lambda x: x

  if fitter := field.metadata.get("fitter", None):
    return fitter

  logger.debug(msg=f"No fitter defined for {field_name}; using simple type check")

  def fit_by_type(value):
    t = field.type
    if origin_type := get_origin(t):  # Some sort of complex type, e.g. list[str]
      t = origin_type  # Get the basic type
    if not isinstance(value, t):
      return t(value)
    return value

  return fit_by_type


def get_scaf_folder(root: Path) -> Path:
  return root / SCAF_FOLDER_NAME
