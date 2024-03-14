from pathlib import Path
from typing import Dict, Protocol

DictSI = Dict[str, int]


class Collector(Protocol):
    def collect(self, bin_dir: Path) -> Dict[str, DictSI]: ...
