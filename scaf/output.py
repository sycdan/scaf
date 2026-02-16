import json
import logging
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from pprint import pprint
from uuid import UUID

# Colors for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

logger = logging.getLogger(__name__)


def print_success(msg: str) -> None:
  """Print success message in green"""
  print(f"{GREEN}✓ {NC} {msg}", file=sys.stderr)


class JSONEncoder(json.JSONEncoder):
  """Custom JSON encoder that handles dataclasses, Path objects, and other common types."""

  def default(self, obj):
    if is_dataclass(obj):
      return asdict(obj)  # type: ignore
    elif isinstance(obj, Path):
      return obj.as_posix()
    elif isinstance(obj, UUID):
      return str(obj)
    elif isinstance(obj, datetime):
      return obj.isoformat()
    elif isinstance(obj, set):
      return list(obj)
    elif hasattr(obj, "__dict__"):
      return obj.__dict__
    else:
      # Let the base class handle other types
      return super().default(obj)


def print_result(result) -> None:
  """Print action response as JSON if possible, fallback to pprint if serialization fails."""
  if result is None:
    return

  try:
    json_output = json.dumps(result, cls=JSONEncoder, indent=2, ensure_ascii=False)
    print(json_output)
  except (TypeError, ValueError) as e:
    # JSON serialization failed, fall back to pprint
    logger.warning(f"JSON serialization failed: {e}. Using pprint fallback.")
    pprint(result)
