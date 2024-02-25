from typing import Protocol
from pathlib import Path


class Patcher(Protocol):
    def patch(self, test_dir: Path, dst_dir: Path):
        ...
