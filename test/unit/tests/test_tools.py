import pytest


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
