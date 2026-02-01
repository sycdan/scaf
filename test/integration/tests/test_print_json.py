import json
from uuid import UUID

from scaf import config


def test(sandbox):
  response = sandbox.run_scaf(config.REPO_ROOT, "--call=example/myriad/get")
  data = json.loads(response.stdout)
  assert UUID(data["guid"])
  assert data["boolean"] is True
  assert data["integer"] == 42
  assert data["text"] == "hello"
  assert abs(data["float"] - 3.14) < 0.0001
