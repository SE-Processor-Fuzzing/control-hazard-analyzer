import json
from typing import Dict, Protocol
from pathlib import Path


class IPacker(Protocol):
    def pack(self, out_dir: Path, analyzed_data: Dict[str, Dict]):
        ...


class Packer:
    def pack(self, out_dir: Path, analyzed_data: Dict[str, Dict]):
        out_dir.mkdir(parents=True, exist_ok=True)
        for key in analyzed_data:
            with open(out_dir.joinpath(key + ".data"), "wt") as writter:
                writter.write(json.dumps(analyzed_data[key]))
