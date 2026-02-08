import json
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


def print_info(msg: str) -> None:
  """Print status message in blue"""
  print(f"{BLUE}► {NC} {msg}", file=sys.stderr)


def print_success(msg: str) -> None:
  """Print success message in green"""
  print(f"{GREEN}✓ {NC} {msg}", file=sys.stderr)


def print_warning(msg: str) -> None:
  """Print warning message in yellow to stderr"""
  print(f"{YELLOW}⚠ {NC} {msg}", file=sys.stderr)


def print_error(msg: str) -> None:
  """Print error message in red to stderr"""
  print(f"{RED}✗ {NC} {msg}", file=sys.stderr)


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
    elif hasattr(obj, "__dict__"):
      return obj.__dict__
    else:
      # Let the base class handle other types
      return super().default(obj)


def print_result(response) -> None:
  """Print action response as JSON if possible, fallback to pprint if serialization fails."""
  if response is None:
    return

  try:
    json_output = json.dumps(response, cls=JSONEncoder, indent=2, ensure_ascii=False)
    print(json_output)
  except (TypeError, ValueError) as e:
    # JSON serialization failed, fall back to pprint
    print_warning(f"JSON serialization failed: {e}. Using pprint fallback.")
    pprint(response)
