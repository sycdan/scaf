import ast
import json
import logging
import os
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from scaf.deck.entity import Deck
from scaf.user.serve.command import Serve

logger = logging.getLogger(__name__)

_MAX_DISCOVER_DEPTH = 10

_PYTEST_RUN_OPTS = [
  "--override-ini=addopts=",
  "--override-ini=python_files=test_fixtures.py",
  "--override-ini=testpaths=",
  "--import-mode=importlib",
  "-p",
  "no:cacheprovider",
  "-p",
  "no:logging",
  "-p",
  "no:capture",
  "-q",
]


class FileWatcher:
  """Background thread that polls .py files under a directory and reloads changed modules."""

  def __init__(self, watch_dir, poll_interval: float = 1.0):
    self._watch_dir = watch_dir
    self._poll_interval = poll_interval
    self._mtimes: dict = {}
    self._stop = threading.Event()
    self._thread: threading.Thread | None = None

  def start(self):
    self._thread = threading.Thread(target=self._run, daemon=True, name="scaf-filewatcher")
    self._thread.start()

  def stop(self):
    self._stop.set()

  def _run(self):
    while not self._stop.wait(self._poll_interval):
      self._poll()

  def _poll(self):
    try:
      py_files = list(self._watch_dir.rglob("*.py"))
    except OSError:
      return
    for path in py_files:
      try:
        mtime = path.stat().st_mtime
      except OSError:
        continue
      path_str = str(path.resolve())
      if path_str in self._mtimes and self._mtimes[path_str] != mtime:
        self._reload(path_str)
      self._mtimes[path_str] = mtime

  def _reload(self, path_str: str):
    to_reload = [
      (name, mod)
      for name, mod in list(sys.modules.items())
      if hasattr(mod, "__file__")
      and mod.__file__
      and str(Path(mod.__file__).resolve()) == path_str
    ]
    logger.debug("Reloading %s — found %d matching module(s)", path_str, len(to_reload))
    for name, mod in to_reload:
      try:
        source = Path(path_str).read_text(encoding="utf-8")
        code = compile(source, path_str, "exec")
        exec(code, mod.__dict__)  # noqa: S102
        logger.info("Reloaded module %s (%s)", name, path_str)
      except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to reload module %s: %s", name, exc)


class _Runner:
  """In-process pytest plugin: tracks pass/fail outcome for a single test run."""

  def __init__(self):
    self.outcome = None

  def pytest_runtest_logreport(self, report):
    if report.failed:
      self.outcome = "fail"
    elif report.when == "call" and report.passed and self.outcome is None:
      self.outcome = "pass"


_INDEX_HTML = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>scaf dev server</title>
<style>
  *{box-sizing:border-box}
  body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;background:#fafafa;color:#111}
  h1{font-size:1.4rem;margin-bottom:1.5rem}
  label{display:block;font-weight:600;margin:.9rem 0 .3rem}
  textarea,select,input[type=text]{width:100%;padding:.45rem .6rem;border:1px solid #ccc;border-radius:4px;font-size:.95rem;font-family:inherit}
  textarea{height:140px;font-family:monospace;resize:vertical}
  #tests-section{margin-top:1rem}
  .test-row{display:flex;align-items:center;gap:.7rem;margin:.4rem 0}
  .test-row input[type=checkbox]{width:auto}
  .test-row select{width:auto;padding:.25rem .4rem}
  button{margin-top:1.2rem;padding:.5rem 1.4rem;background:#0066cc;color:#fff;border:none;border-radius:4px;font-size:1rem;cursor:pointer}
  button:disabled{opacity:.5;cursor:default}
  #results{margin-top:1.5rem}
  table{width:100%;border-collapse:collapse;font-size:.9rem}
  th,td{text-align:left;padding:.4rem .6rem;border-bottom:1px solid #ddd}
  th{background:#f0f0f0}
  .pass{color:#1a7f37;font-weight:600}
  .fail{color:#cf222e;font-weight:600}
  .err{color:#888;font-style:italic}
</style>
</head>
<body>
<h1>scaf dev server</h1>

<label for="action-select">Action</label>
<select id="action-select">
  <option value="">— loading actions… —</option>
</select>

<label for="payload-input">Payload (JSON)</label>
<textarea id="payload-input" placeholder="{}">{}</textarea>

<label for="description-input">Description (optional)</label>
<input type="text" id="description-input" placeholder="e.g. bug reported 2026-02-28">

<div id="tests-section" hidden>
  <label>Tests</label>
  <div id="tests-list"></div>
</div>

<button id="submit-btn" disabled>Run</button>

<div id="results"></div>

<script>
(function () {
  const actionSel = document.getElementById('action-select');
  const payloadTA = document.getElementById('payload-input');
  const descInput = document.getElementById('description-input');
  const testsSection = document.getElementById('tests-section');
  const testsList = document.getElementById('tests-list');
  const submitBtn = document.getElementById('submit-btn');
  const resultsDiv = document.getElementById('results');

  // ── Load actions ──────────────────────────────────────────────────────────
  fetch('/actions')
    .then(r => r.json())
    .then(actions => {
      actionSel.innerHTML = '<option value="">— select an action —</option>';
      actions.forEach(p => {
        const opt = document.createElement('option');
        opt.value = opt.textContent = p;
        actionSel.appendChild(opt);
      });
    })
    .catch(() => { actionSel.innerHTML = '<option value="">— failed to load actions —</option>'; });

  // ── Load tests when action changes ────────────────────────────────────────
  actionSel.addEventListener('change', () => {
    const action = actionSel.value;
    testsList.innerHTML = '';
    submitBtn.disabled = true;
    if (!action) { testsSection.hidden = true; return; }
    fetch('/actions/' + action + '/tests')
      .then(r => r.json())
      .then(nodes => {
        testsSection.hidden = false;
        testsList.innerHTML = '';
        if (nodes.length === 0) {
          testsList.innerHTML = '<p class="err">No tests found for this action. Add <code>test_fixtures.py</code> files alongside <code>handler.py</code> to enable test execution.</p>';
          submitBtn.disabled = true;
          return;
        }
        nodes.forEach(nodeId => {
          const name = nodeId.split('::').pop();
          const row = document.createElement('div');
          row.className = 'test-row';
          row.innerHTML =
            '<input type="checkbox" checked data-node="' + esc(nodeId) + '" data-name="' + esc(name) + '">' +
            '<span>' + esc(nodeId) + '</span>' +
            '<select data-expect>' +
              '<option value="pass">expect: pass</option>' +
              '<option value="fail">expect: fail</option>' +
            '</select>';
          testsList.appendChild(row);
        });
        submitBtn.disabled = false;
      })
      .catch(() => { testsSection.hidden = true; });
  });

  // ── Submit ─────────────────────────────────────────────────────────────────
  submitBtn.addEventListener('click', () => {
    const action = actionSel.value;
    if (!action) return;

    let payload;
    try { payload = JSON.parse(payloadTA.value || '{}'); }
    catch { resultsDiv.innerHTML = '<p class="fail">Invalid JSON in payload.</p>'; return; }

    const tests = [];
    testsList.querySelectorAll('.test-row').forEach(row => {
      const chk = row.querySelector('input[type=checkbox]');
      if (!chk.checked) return;
      const name = chk.dataset.name;
      const expect = row.querySelector('[data-expect]').value;
      tests.push({ name, expect });
    });

    submitBtn.disabled = true;
    submitBtn.textContent = 'Running…';
    resultsDiv.innerHTML = '';

    fetch('/actions/' + action + '/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload, description: descInput.value, tests }),
    })
      .then(r => r.json())
      .then(data => renderResults(data.results || []))
      .catch(e => { resultsDiv.innerHTML = '<p class="fail">Request failed: ' + esc(String(e)) + '</p>'; })
      .finally(() => { submitBtn.disabled = false; submitBtn.textContent = 'Run'; });
  });

  // ── Helpers ────────────────────────────────────────────────────────────────
  function renderResults(results) {
    if (!results.length) { resultsDiv.innerHTML = '<p class="err">No tests selected.</p>'; return; }
    let html = '<table><thead><tr><th>Test</th><th>Expected</th><th>Actual</th><th>Verdict</th></tr></thead><tbody>';
    results.forEach(r => {
      const verdict = r.passed
        ? '<span class="pass">&#10003; OK</span>'
        : '<span class="fail">&#10007; MISMATCH</span>';
      const actual = r.actual === 'pass'
        ? '<span class="pass">pass</span>'
        : '<span class="fail">fail</span>';
      html += '<tr><td>' + esc(r.test) + '</td><td>' + esc(r.expected) + '</td><td>' + actual + '</td><td>' + verdict + '</td></tr>';
    });
    html += '</tbody></table>';
    resultsDiv.innerHTML = html;
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
})();
</script>
</body>
</html>
"""


def _make_handler_class(deck: Deck):
  """Return a BaseHTTPRequestHandler subclass with the Serve command baked in."""

  class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
      logger.debug(format, *args)

    def _send_json(self, data, status: int = 200):
      body = json.dumps(data).encode()
      self.send_response(status)
      self.send_header("Content-Type", "application/json")
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      self.wfile.write(body)

    def _send_html(self, body: bytes, status: int = 200):
      self.send_response(status)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      self.wfile.write(body)

    def do_GET(self):
      parsed = urlparse(self.path)
      path = parsed.path.rstrip("/")

      if path == "/actions":
        self._handle_get_actions()
      elif path.startswith("/actions/") and path.endswith("/tests"):
        action_path = path[len("/actions/") : -len("/tests")]
        self._handle_get_action_tests(action_path)
      else:
        self._send_html(_INDEX_HTML.encode("utf-8"))

    def do_POST(self):
      parsed = urlparse(self.path)
      path = parsed.path.rstrip("/")

      if path.startswith("/actions/") and path.endswith("/run"):
        action_path = path[len("/actions/") : -len("/run")]
        self._handle_post_action_run(action_path)
      else:
        self._send_json({"error": "Not found"}, status=404)

    def _handle_post_action_run(self, action_path: str):
      content_length = int(self.headers.get("Content-Length", 0))
      raw = self.rfile.read(content_length)
      try:
        body = json.loads(raw)
      except json.JSONDecodeError as exc:
        self._send_json({"error": f"Invalid JSON: {exc}"}, status=400)
        return
      try:
        self._run_action_tests(action_path, body)
      except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error in POST /run")
        self._send_json({"error": str(exc)}, status=500)

    def _run_action_tests(self, action_path: str, body: dict):
      payload = body.get("payload", {})
      tests = body.get("tests", [])

      # Derive deterministic fixture filename from payload
      canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
      fixture_id = uuid.uuid5(uuid.NAMESPACE_DNS, canonical)
      fixture_filename = f"{fixture_id.hex}.json"

      # Write fixture (2-space indent, keys unsorted)
      description = body.get("description", "")
      action_folder = deck.root / action_path
      fixtures_dir = action_folder / "fixtures"
      fixtures_dir.mkdir(parents=True, exist_ok=True)
      expectations = {
        t.get("name", "").split("::")[-1]: t.get("expect", "pass") == "pass" for t in tests
      }
      fixture_data = {"payload": payload, "description": description, "expectations": expectations}
      (fixtures_dir / fixture_filename).write_text(
        json.dumps(fixture_data, indent=2), encoding="utf-8"
      )

      # Run each requested test in-process with SCAF_FIXTURE set
      try:
        import pytest  # noqa: PLC0415
      except ImportError:
        self._send_json({"error": "pytest is not installed. Run: pip install pytest"}, status=500)
        return
      old_fixture = os.environ.get("SCAF_FIXTURE")
      old_no_xfail = os.environ.get("SCAF_NO_XFAIL")
      os.environ["SCAF_FIXTURE"] = fixture_filename
      os.environ["SCAF_NO_XFAIL"] = "1"
      try:
        results = []
        for test_spec in tests:
          test_name = test_spec.get("name", "")
          expected = test_spec.get("expect", "pass")
          func_name = test_name.split("::")[-1]
          runner = _Runner()
          pytest.main(
            [
              str(action_folder),
              "-k",
              func_name,
              "--rootdir",
              str(action_folder),
            ]
            + _PYTEST_RUN_OPTS,
            plugins=[runner],
          )
          actual = runner.outcome or "fail"
          results.append(
            {
              "test": test_name,
              "expected": expected,
              "actual": actual,
              "passed": actual == expected,
            }
          )
      finally:
        if old_fixture is None:
          os.environ.pop("SCAF_FIXTURE", None)
        else:
          os.environ["SCAF_FIXTURE"] = old_fixture
        if old_no_xfail is None:
          os.environ.pop("SCAF_NO_XFAIL", None)
        else:
          os.environ["SCAF_NO_XFAIL"] = old_no_xfail

      self._send_json({"results": results})

    def _handle_get_actions(self):
      from scaf.user.discover.handler import find_available_actions

      actions = find_available_actions(deck.root, _MAX_DISCOVER_DEPTH)
      self._send_json([p.as_posix() for p in actions])

    def _handle_get_action_tests(self, action_path: str):
      tests_file = deck.root / action_path / "test_fixtures.py"
      if not tests_file.exists():
        self._send_json([])
        return
      try:
        tree = ast.parse(tests_file.read_text(encoding="utf-8"))
      except SyntaxError:
        self._send_json([])
        return
      node_ids = [
        f"test_fixtures.py::{node.name}"
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
      ]
      self._send_json(node_ids)

  return _Handler


def make_server(deck: Deck, port: int, poll_interval: float = 1.0) -> HTTPServer:
  """Create an HTTPServer and start a FileWatcher background thread."""
  handler_cls = _make_handler_class(deck)
  server = HTTPServer(("127.0.0.1", port), handler_cls)

  watcher = FileWatcher(deck.root, poll_interval=poll_interval)
  watcher.start()

  return server


def handle(command: Serve) -> None:
  server = make_server(command.deck, command.port)
  host, port = server.server_address[0], server.server_address[1]
  print(f"scaf dev server listening on http://{host}:{port}", file=sys.stderr)
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    logger.info("Server stopped.")
  finally:
    server.server_close()
