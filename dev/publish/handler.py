import logging
import subprocess
import sys
from pathlib import Path

from dev.publish.command import Publish

logger = logging.getLogger(__name__)


def load_env(path: Path) -> dict:
  env = {}
  if not path.exists():
    return env
  for line in path.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
      continue
    key, _, value = line.partition("=")
    env[key.strip()] = value.strip().strip('"').strip("'")
  return env


def handle(command: Publish) -> dict:
  root = Path(".")
  env = load_env(root / ".env")

  repository = env.get("TWINE_REPOSITORY", "testpypi")
  password = env.get("TWINE_PASSWORD")

  if not password:
    raise RuntimeError("TWINE_PASSWORD not set in .env")

  # Read package name from pyproject.toml
  import tomllib

  with open(root / "pyproject.toml", "rb") as f:
    pkg_name = tomllib.load(f)["project"]["name"]

  version = None
  try:
    from packaging.version import Version

    import importlib
    import scaf as _scaf

    importlib.reload(_scaf)
    version = str(Version(_scaf.__version__))  # normalize: "2026.03.01.0001" → "2026.3.1.1"
  except Exception:
    pass

  if not command.skip_build:
    existing = list((root / "dist").glob(f"{pkg_name}-{version}*")) if version else []
    if existing:
      logger.info(f"Existing dist artifacts found for {version}, skipping build.")
    else:
      logger.info("Building package...")
      result = subprocess.run(
        [sys.executable, "-m", "build"],
        capture_output=False,
      )
      if result.returncode != 0:
        raise RuntimeError("Build failed")

  dist_pattern = f"{pkg_name}-{version}*" if version else f"{pkg_name}-*"
  dist_files = sorted((root / "dist").glob(dist_pattern))
  if not dist_files:
    raise RuntimeError(f"No dist files found matching {dist_pattern}")

  logger.info(f"Uploading to {repository}: {[f.name for f in dist_files]}")
  result = subprocess.run(
    [
      sys.executable,
      "-m",
      "twine",
      "upload",
      "--repository",
      repository,
      "-u",
      "__token__",
      "-p",
      password,
      *[str(f) for f in dist_files],
    ],
    capture_output=False,
  )
  if result.returncode != 0:
    raise RuntimeError("Upload failed")

  return {"repository": repository, "files": [f.name for f in dist_files]}
