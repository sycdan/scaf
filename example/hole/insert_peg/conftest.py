import json
import os
from pathlib import Path

import pytest


def pytest_generate_tests(metafunc):
  if "payload" not in metafunc.fixturenames:
    return
  d = Path(metafunc.definition.fspath).parent / "fixtures"
  if name := os.environ.get("SCAF_FIXTURE"):
    files = [d / name] if (d / name).exists() else []
  elif d.exists():
    files = sorted(d.glob("*.json"))
  else:
    files = []
  if not files:
    return
  params = []
  for f in files:
    data = json.loads(Path(f).read_text())
    test_name = metafunc.function.__name__
    expected = data.get("expectations", {}).get(test_name, True)
    marks = (
      [pytest.mark.xfail(strict=True, reason=f"fixture expects {test_name} to fail")]
      if expected is False and not os.environ.get("SCAF_NO_XFAIL")
      else []
    )
    params.append(pytest.param(data["payload"], marks=marks, id=Path(f).stem))
  metafunc.parametrize("payload", params)
