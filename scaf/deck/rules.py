from pathlib import Path


def fit_root(value: Path | str) -> Path:
  if isinstance(value, str):
    value = Path(value.strip())
  elif not isinstance(value, Path):
    raise ValueError(f"must be str or Path, got {type(value)}")
  if not value.is_absolute():
    value = Path.cwd() / value
  if not value.is_dir():
    value = value.parent
  return value


def must_be_real_dir(scaf_folder: Path):
  if not scaf_folder.exists() or not scaf_folder.is_dir():
    raise ValueError(
      f"{scaf_folder} must be a real directory.\n💡 Run 'scaf init' in {scaf_folder.parent}."
    )
