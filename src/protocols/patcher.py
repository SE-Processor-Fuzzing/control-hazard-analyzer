from pathlib import Path
from typing import Protocol


class Patcher(Protocol):
    def patch(self, test_dir: Path, dst_dir: Path) -> None: ...
