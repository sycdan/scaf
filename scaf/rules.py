import logging

from scaf.errors import FittingError
from scaf.tools import get_fitter

logger = logging.getLogger(__name__)


def values_must_fit(instance: object):
  data_class = type(instance)
  try:
    fields = getattr(data_class, "__dataclass_fields__")
  except AttributeError:
    raise TypeError(f"{data_class} is not a dataclass")

  for field_name in fields.keys():
    if fitter := get_fitter(data_class, field_name):
      value = instance.__dict__[field_name]
      try:
        instance.__dict__[field_name] = fitter(value)
      except (ValueError, TypeError) as e:
        raise FittingError(
          f"{fitter.__name__} failed: {data_class.__name__}.{field_name} {e}"
        ) from e
