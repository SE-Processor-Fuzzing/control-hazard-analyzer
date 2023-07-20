from typing import Dict, Protocol
from pathlib import Path


class IProfiler(Protocol):
    def profile(self, test_dir: Path) -> Dict[str, Dict]:
        ...
