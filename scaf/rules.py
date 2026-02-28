import logging

from scaf.errors import FittingError
from scaf.tools import get_fitter

logger = logging.getLogger(__name__)


def values_must_fit(instance: object):
  logger.debug(f"👋 {values_must_fit.__name__}(instance=%r)", instance)
  data_class = type(instance)
  try:
    fields = getattr(data_class, "__dataclass_fields__")
  except AttributeError:
    raise TypeError(f"{data_class} is not a dataclass")

  for field_name, field in fields.items():
    if not field.init:
      continue
    if fitter := get_fitter(data_class, field_name):
      value = instance.__dict__[field_name]
      logger.debug(f"Fitting {value=!r} using {fitter}")
      try:
        instance.__dict__[field_name] = fitter(value)
      except (ValueError, TypeError) as e:
        raise FittingError(
          f"{fitter.__name__} failed: {data_class.__name__}.{field_name} {e}"
        ) from e
