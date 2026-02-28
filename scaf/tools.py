"""May touch filesystem, but not DB or network."""

import importlib.util
import inspect
import json
import logging
import re
import types
import typing
from dataclasses import Field
from datetime import date, datetime, time
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import get_args, get_origin
from zoneinfo import ZoneInfo

from scaf.config import SCAF_FOLDER_NAME
from scaf.output import JSONEncoder

logger = logging.getLogger(__name__)

_UTC = ZoneInfo("UTC")


def _local_timezone() -> ZoneInfo:
  """Detect the system local timezone, falling back to UTC with a warning."""
  try:
    return ZoneInfo("localtime")
  except Exception:
    logger.warning("Could not detect local timezone; defaulting to UTC")
    return _UTC


def parse_datetime(when: datetime | str, where: ZoneInfo | str | None = None) -> datetime:
  """Parse a datetime from a string or datetime, applying timezone if naive.

  If `where` is None, the system local timezone is used (UTC with a warning if
  the local timezone cannot be detected).

  Raises ValueError for unparseable strings or invalid timezone names.
  """
  if not where:
    where = _local_timezone()

  try:
    if not isinstance(where, ZoneInfo):
      where = ZoneInfo(where.strip())
  except Exception as e:
    raise ValueError(f"Invalid timezone: {where}") from e

  try:
    if not isinstance(when, datetime):
      s = when.strip().replace("Z", "+00:00")
      try:
        when = datetime.fromisoformat(s)
      except ValueError:
        # Try parsing as a time-only string and assume today's date
        t = time.fromisoformat(s)
        when = datetime.combine(date.today(), t)
  except Exception as e:
    raise ValueError(f"Invalid datetime: {when}") from e

  if when.tzinfo is None:
    when = when.replace(tzinfo=where)

  return when.astimezone(tz=where)


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


def get_acceptable_types(field: Field):
  """Returns (`canonical_type`, `proxy_type`, `optional`) for a dataclass field.

  `canonical_type`:
    The primary type expected by the internal domain.
  `proxy_type`:
    A type the domain can use to construct the canonical type from a single string input.
    If the type definition is not a Union, this will be the same as `canonical_type`.
  `optional`:
    Whether the field can be None.

  Examples:
    - `x: MyDomainType` -> `canonical_type` = `proxy_type` = `MyDomainType`.
    - `x: MyDomainType | MyDomainTypeRef` -> `canonical_type` = `MyDomainType`; `proxy_type` = `MyDomainTypeRef`.
    - `x: MyDomainTypeRef | None` -> `canonical_type` = `proxy_type` = `MyDomainTypeRef`; `optional` = True.
  """
  t = field.type

  if isinstance(t, types.UnionType) or get_origin(t) is typing.Union:
    args = get_args(t)
    optional = type(None) in args
    non_none_types = [a for a in args if a is not type(None)]
    canonical_type = non_none_types[0]
    proxy_type = non_none_types[-1]
    return canonical_type, proxy_type, optional

  return t, t, False


def get_fitter(for_class: type, field_name: str):
  logger.debug(f"👋 {get_fitter.__name__} {for_class=} {field_name=}")
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

  # 1. Convention: fit_<field_name> in the sibling rules module
  try:
    class_file = inspect.getfile(for_class)
    logger.debug(f"{class_file=}")
    rules_file = Path(class_file).parent / "rules.py"
    logger.debug(f"{rules_file=}")
    if rules_file.exists():
      spec = importlib.util.spec_from_file_location(rules_file.as_posix(), str(rules_file))
      if spec and spec.loader:
        rules_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rules_mod)
        if fn := getattr(rules_mod, f"fit_{field_name}", None):
          if callable(fn):
            logger.debug(f"Using {rules_file}::fit_{field_name} for {field_name}")
            return fn
  except (TypeError, OSError):
    pass

  # 2. Explicit fitter in field metadata
  if fitter := field.metadata.get("fitter", None):
    logger.warning(f"Using deprecated metadata {fitter=} for {field_name=}")
    return fitter

  logger.debug(msg=f"No fitter defined for {field_name}; using simple type check")

  def fit_by_type(value):
    domain_type, proxy_type, optional = get_acceptable_types(field)

    if value is None:
      if optional:
        return None
      else:
        raise ValueError(f"{field_name} cannot be None")

    if not isinstance(domain_type, type):
      logger.warning(f"Unable to infer domain type for {field_name}. Skipping fitting.")
      return value

    if origin_type := get_origin(domain_type):  # e.g. list[str]
      domain_type = origin_type

    if isinstance(value, domain_type):
      return value
    elif domain_type is datetime:
      return parse_datetime(value)

    return proxy_type(value)  # type: ignore

  return fit_by_type


def get_scaf_folder(root: Path) -> Path:
  return root / SCAF_FOLDER_NAME


def read_json_file(path: Path) -> dict:
  if not path.exists():
    return {}

  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except json.JSONDecodeError as e:
    logger.error(f"Failed to parse JSON file at {path}: {e}")
    return {}


def write_json_file(path: Path, data: dict) -> None:
  path.write_text(json.dumps(data, indent=2, cls=JSONEncoder) + "\n", encoding="utf-8")
