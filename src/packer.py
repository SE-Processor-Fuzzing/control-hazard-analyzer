from typing import Dict, Protocol
from pathlib import Path


class IPacker(Protocol):
    def pack(self, out_dir: Path, analyzed_data: Dict[str, Dict]):
        ...
