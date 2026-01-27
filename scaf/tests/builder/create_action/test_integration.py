import shutil
import uuid

import pytest

from scaf import config, cli

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def cleanup_example_dirs():
  """Cleanup after test regardless of success/failure."""
  yield
  for pattern in ["gen/x*", "proto/gen/x*", "tests/gen/x*"]:
    for path in config.ROOT_DIR.glob(pattern):
      if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


def test_create_action_is_idempotent():
  new_domain_dir = config.ROOT_DIR / "gen" / f"x{uuid.uuid4().hex[:8]}"
  action_args = [
    new_domain_dir.relative_to(config.ROOT_DIR).as_posix(),
    "command",
  ]

  # 1. First run - creates files
  cli.main(["scaf/builder/create_action"] + action_args)

  handler_file = new_domain_dir / "handler.py"
  assert handler_file.exists()
  original_content = handler_file.read_text()

  # 2. Modify a file
  custom_content = original_content + "\n# Custom modification"
  handler_file.write_text(custom_content)

  # 3. Second run - should not overwrite
  cli.main(["scaf/builder/create_action"] + action_args)

  # 4. Verify content is preserved
  assert handler_file.read_text() == custom_content
