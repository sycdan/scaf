import importlib.util
import json
import sys
import threading
import time
import urllib.request
import uuid
from pathlib import Path

from test.integration.conftest import Sandbox


def test_serve_help_exits_0_and_mentions_port(sandbox: Sandbox):
  success, stdout, stderr = sandbox.scaf("serve", "--help")

  assert success, f"Expected 'scaf serve --help' to exit 0\nstdout={stdout}\nstderr={stderr}"
  assert "port" in stdout, f"Expected 'port' in help output\nstdout={stdout}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _start_test_server(deck_root: Path, port: int = 0):
  """Start server on a background thread. Returns (server, port)."""
  from scaf.deck.entity import Deck
  from scaf.user.serve.handler import make_server

  deck = Deck(root=deck_root)
  server = make_server(deck, port)
  actual_port = server.server_address[1]
  t = threading.Thread(target=server.serve_forever, daemon=True)
  t.start()
  return server, actual_port


def _get_json(port: int, path: str):
  url = f"http://127.0.0.1:{port}{path}"
  with urllib.request.urlopen(url, timeout=5) as resp:
    return json.loads(resp.read())


# ---------------------------------------------------------------------------
# HTTP server + action discovery endpoints
# ---------------------------------------------------------------------------


def test_get_actions_returns_json_list_of_action_paths(sandbox: Sandbox):
  """GET /actions returns a non-empty JSON list of action paths."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  server, port = _start_test_server(sandbox.root)
  try:
    data = _get_json(port, "/actions")
  finally:
    server.shutdown()

  assert isinstance(data, list), f"Expected list, got {type(data)}: {data}"
  assert len(data) > 0, "Expected at least one action"
  assert all(isinstance(p, str) for p in data), f"Non-string items: {data}"
  assert any("myriad" in p for p in data), f"Expected myriad action in {data}"


def test_get_action_tests_returns_test_node_ids(sandbox: Sandbox):
  """GET /actions/<path>/tests lists pytest node IDs for an action with tests."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  action_rel = "example/myriad/get"
  sandbox.write(
    f"{action_rel}/test_fixtures.py",
    "def test_always_passes():\n    assert True\n\ndef test_another():\n    assert 1 + 1 == 2\n",
  )

  server, port = _start_test_server(sandbox.root)
  try:
    data = _get_json(port, f"/actions/{action_rel}/tests")
  finally:
    server.shutdown()

  assert isinstance(data, list), f"Expected list, got {type(data)}: {data}"
  assert len(data) >= 2, f"Expected at least 2 test node IDs, got: {data}"
  assert any("test_always_passes" in node for node in data), (
    f"Missing test_always_passes in {data}"
  )
  assert any("test_another" in node for node in data), f"Missing test_another in {data}"


# ---------------------------------------------------------------------------
# Payload POST, fixture save, test execution
# ---------------------------------------------------------------------------

_CONFTEST_CONTENT = """\
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
"""

_TEST_CONTENT = """\
def test_payload_has_value(payload):
  assert "value" in payload


def test_payload_value_positive(payload):
  assert payload.get("value", 0) > 0
"""


def _post_json(port: int, path: str, body: dict):
  encoded = json.dumps(body).encode()
  req = urllib.request.Request(
    f"http://127.0.0.1:{port}{path}",
    data=encoded,
    headers={"Content-Type": "application/json"},
    method="POST",
  )
  with urllib.request.urlopen(req, timeout=30) as resp:
    return json.loads(resp.read())


def test_post_action_run_saves_fixture_and_returns_results(sandbox: Sandbox):
  """POST /actions/<path>/run writes fixture file and returns per-test pass/fail results."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  action_rel = "example/myriad/get"
  sandbox.write(f"{action_rel}/conftest.py", _CONFTEST_CONTENT)
  sandbox.write(f"{action_rel}/test_fixtures.py", _TEST_CONTENT)

  payload_data = {"value": 42}
  canonical = json.dumps(payload_data, separators=(",", ":"), sort_keys=True)
  fixture_id = uuid.uuid5(uuid.NAMESPACE_DNS, canonical).hex

  server, port = _start_test_server(sandbox.root)
  try:
    result = _post_json(
      port,
      f"/actions/{action_rel}/run",
      {
        "payload": payload_data,
        "description": "regression from 2026-02-28",
        "tests": [
          {"name": "test_payload_has_value", "expect": "pass"},
          {"name": "test_payload_value_positive", "expect": "pass"},
        ],
      },
    )
  finally:
    server.shutdown()

  # Fixture file must exist
  fixture_path = sandbox.root / action_rel / "fixtures" / f"{fixture_id}.json"
  assert fixture_path.exists(), f"Fixture not written at {fixture_path}"
  fixture_json = json.loads(fixture_path.read_text())
  assert fixture_json["payload"] == payload_data
  assert fixture_json.get("expectations") == {
    "test_payload_has_value": True,
    "test_payload_value_positive": True,
  }

  # Results shape
  assert "results" in result, f"Missing 'results' key: {result}"
  results = result["results"]
  assert len(results) == 2, f"Expected 2 results, got: {results}"

  for r in results:
    assert r["actual"] == "pass", f"Test unexpectedly failed: {r}"
    assert r["passed"] is True, f"Expected passed=True: {r}"


def test_post_action_run_reports_failing_test(sandbox: Sandbox):
  """POST /actions/<path>/run correctly reports a test that fails as expected."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  action_rel = "example/myriad/get"
  sandbox.write(f"{action_rel}/conftest.py", _CONFTEST_CONTENT)
  sandbox.write(
    f"{action_rel}/test_fixtures.py",
    "def test_always_fails(payload):\n  assert False, 'intentional failure'\n",
  )

  payload_data = {"value": 1}

  server, port = _start_test_server(sandbox.root)
  try:
    result = _post_json(
      port,
      f"/actions/{action_rel}/run",
      {
        "payload": payload_data,
        "tests": [{"name": "test_always_fails", "expect": "fail"}],
      },
    )
  finally:
    server.shutdown()

  results = result["results"]
  assert len(results) == 1
  r = results[0]
  assert r["actual"] == "fail", f"Expected actual=fail: {r}"
  assert r["passed"] is True, f"Expected passed=True (expected fail, got fail): {r}"

  fixture_path = (
    sandbox.root
    / action_rel
    / "fixtures"
    / (
      uuid.uuid5(
        uuid.NAMESPACE_DNS, json.dumps({"value": 1}, separators=(",", ":"), sort_keys=True)
      ).hex
      + ".json"
    )
  )
  assert json.loads(fixture_path.read_text()).get("expectations") == {"test_always_fails": False}


# ---------------------------------------------------------------------------
# Frontend UI
# ---------------------------------------------------------------------------


def _get_html(port: int, path: str = "/") -> tuple[int, str, str]:
  """Return (status_code, content_type, body) for a GET request."""
  url = f"http://127.0.0.1:{port}{path}"
  with urllib.request.urlopen(url, timeout=5) as resp:
    return resp.status, resp.headers.get("Content-Type", ""), resp.read().decode()


def test_root_returns_html_page(sandbox: Sandbox):
  """GET / returns a valid HTML page with the expected UI elements."""
  sandbox.add_example_domain()
  sandbox.scaf_init()

  server, port = _start_test_server(sandbox.root)
  try:
    status, content_type, body = _get_html(port, "/")
  finally:
    server.shutdown()

  assert status == 200, f"Expected 200, got {status}"
  assert "text/html" in content_type, f"Expected text/html content-type, got {content_type}"

  # Payload textarea
  assert "<textarea" in body, "Missing payload textarea"

  # Description input
  assert 'type="text"' in body or 'name="description"' in body, "Missing description field"

  # Action selector dropdown
  assert "<select" in body, "Missing action selector <select>"

  # Submit button
  assert "<button" in body or 'type="submit"' in body, "Missing submit button"

  # JS must reference the API endpoints it will call
  assert "/actions" in body, "Missing /actions API reference in JS"


# ---------------------------------------------------------------------------
# Hot reload
# ---------------------------------------------------------------------------


def test_file_watcher_reloads_module_after_file_change(tmp_path):
  """FileWatcher detects a .py file change and reloads the corresponding sys.modules entry."""
  from scaf.user.serve.handler import FileWatcher

  mod_file = tmp_path / "hotmod.py"
  mod_file.write_text("VALUE = 'v1'\n", encoding="utf-8")

  # Register module in sys.modules manually
  spec = importlib.util.spec_from_file_location("hotmod", mod_file)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  sys.modules["hotmod"] = mod

  try:
    watcher = FileWatcher(tmp_path, poll_interval=0.05)
    watcher.start()
    try:
      assert sys.modules["hotmod"].VALUE == "v1"
      time.sleep(0.15)  # let watcher capture initial mtimes
      mod_file.write_text("VALUE = 'v2'\n", encoding="utf-8")
      time.sleep(0.4)  # allow watcher to detect change and reload

      assert sys.modules["hotmod"].VALUE == "v2", (
        f"FileWatcher did not reload 'hotmod': VALUE is still {sys.modules['hotmod'].VALUE!r}"
      )
    finally:
      watcher.stop()
  finally:
    sys.modules.pop("hotmod", None)


def _start_watcher(watch_dir: Path, poll_interval: float = 0.05):
  """Start a FileWatcher on a directory and return it."""
  from scaf.user.serve.handler import FileWatcher

  watcher = FileWatcher(watch_dir, poll_interval=poll_interval)
  watcher.start()
  return watcher


def test_server_uses_reloaded_module_after_file_change(sandbox: Sandbox, tmp_path):
  """When an action file changes while the server runs, the server's FileWatcher reloads
  the module in sys.modules so subsequent runs see the updated code."""
  ver_file = tmp_path / "ver.py"
  ver_file.write_text("VERSION = 'v1'\n", encoding="utf-8")

  # Register 'ver' in sys.modules (simulating what an action test run would do)
  sys.path.insert(0, str(ver_file.parent))
  try:
    import ver  # noqa: F401

    assert ver.VERSION == "v1"

    watcher = _start_watcher(tmp_path, poll_interval=0.05)
    try:
      # Allow FileWatcher to capture initial mtimes before we modify the file
      time.sleep(0.15)

      # Modify ver.py while the watcher is running
      ver_file.write_text("VERSION = 'v2'\n", encoding="utf-8")
      time.sleep(0.4)  # allow FileWatcher to detect and reload

      assert sys.modules["ver"].VERSION == "v2", (
        f"FileWatcher did not update sys.modules['ver']: VERSION={sys.modules['ver'].VERSION!r}"
      )
    finally:
      watcher.stop()
  finally:
    sys.modules.pop("ver", None)
    sys.path.remove(str(ver_file.parent))
