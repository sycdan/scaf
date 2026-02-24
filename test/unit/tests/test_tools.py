from datetime import date, time, timezone

import pytest


@pytest.mark.parametrize(
  "time_str",
  [
    "14:30",
    "14:30:00",
    "09:05:59",
    "00:00",
    "23:59:59.999999",
  ],
)
def test_parse_datetime_time_only_assumes_today(time_str):
  from scaf.tools import parse_datetime

  today = date.today()
  result = parse_datetime(time_str)

  assert result.year == today.year
  assert result.month == today.month
  assert result.day == today.day
  t = time.fromisoformat(time_str)
  assert result.hour == t.hour
  assert result.minute == t.minute
  assert result.second == t.second


@pytest.mark.parametrize(
  "time_str,expected_utc_time",
  [
    ("14:30+05:00", time(9, 30, tzinfo=timezone.utc)),
    ("14:30-04:00", time(18, 30, tzinfo=timezone.utc)),
    ("00:00+00:00", time(0, 0, tzinfo=timezone.utc)),
    ("12:00+05:30", time(6, 30, tzinfo=timezone.utc)),
    ("14:30Z", time(14, 30, tzinfo=timezone.utc)),
  ],
)
def test_parse_datetime_time_with_offset_respects_offset(time_str, expected_utc_time):
  from zoneinfo import ZoneInfo

  from scaf.tools import parse_datetime

  result = parse_datetime(time_str, where="UTC")

  assert result.hour == expected_utc_time.hour
  assert result.minute == expected_utc_time.minute
  assert result.second == expected_utc_time.second
  assert result.tzinfo == ZoneInfo("UTC")


@pytest.mark.parametrize(
  "input,expected",
  [
    ("From Title Case", "FromTitleCase"),
    ("from_snake_case", "FromSnakeCase"),
    ("from-slug-case", "FromSlugCase"),
    ("FromCamelCase", "FromCamelCase"),
  ],
)
def test_to_camel_case(input, expected):
  from scaf.tools import to_camel_case

  assert to_camel_case(input) == expected


@pytest.mark.parametrize(
  "input,expected",
  [
    ("From Title Case", "from-title-case"),
    ("from_snake_case", "from-snake-case"),
    ("from-slug-case", "from-slug-case"),
    ("FromCamelCase", "from-camel-case"),
  ],
)
def test_to_slug_case(input, expected):
  from scaf.tools import to_slug_case

  assert to_slug_case(input) == expected


@pytest.mark.parametrize(
  "input,expected",
  [
    ("From Title Case", "from_title_case"),
    ("from_snake_case", "from_snake_case"),
    ("from-slug-case", "from_slug_case"),
    ("FromCamelCase", "from_camel_case"),
  ],
)
def test_to_snake_case(input, expected):
  from scaf.tools import to_snake_case

  assert to_snake_case(input) == expected


@pytest.mark.parametrize(
  "input,expected",
  [
    ("simple", "simple"),
    ("simple/path", "simple.path"),
    ("complex/nested/path", "complex.nested.path"),
    ("deep/very/nested/complex/path", "deep.very.nested.complex.path"),
    ("", Exception),
  ],
)
def test_to_dot_path(input, expected):
  from pathlib import Path

  from scaf.tools import to_dot_path

  path = Path(input)
  if expected is Exception:
    with pytest.raises(Exception):
      to_dot_path(path)
  else:
    assert to_dot_path(path) == expected
