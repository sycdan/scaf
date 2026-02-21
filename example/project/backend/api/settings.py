from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
  host: str = "localhost"
  port: int = 8080
  base: Path = Path("/api")
