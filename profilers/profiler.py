from typing import Protocol
from pathlib import Path


class IProfiler(Protocol):
    def profile(self, dir: Path) -> bool:
        ...
