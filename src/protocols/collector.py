from typing import Dict, Protocol
from pathlib import Path


class Collector(Protocol):
    def collect(self, bin_dir: Path) -> Dict[str, Dict]:
        ...
