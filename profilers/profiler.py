from typing import Dict, Protocol
from pathlib import Path


class IProfiler(Protocol):
    def profile(self, dir: Path) -> Dict[str, Dict]:
        ...
