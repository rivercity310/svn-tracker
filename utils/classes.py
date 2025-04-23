from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppFiles:
    SETTING_FILE: Path = Path.home() / "svn_tracker.yaml"
    