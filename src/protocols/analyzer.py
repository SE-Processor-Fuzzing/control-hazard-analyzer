from typing import Dict, Protocol
from pathlib import Path


class Analyzer(Protocol):
    def analyze(self, test_dir: Path) -> Dict[str, Dict]:
        ...
